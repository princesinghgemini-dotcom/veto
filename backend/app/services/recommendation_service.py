"""
Recommendation service - deterministic product mapping and retailer matching.
"""
import uuid
import math
from typing import Optional, List, Dict
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.diagnosis_repo import (
    DiagnosisRepository,
    GeminiOutputRepository,
    TagRepository
)
from app.repositories.farmer_repo import FarmerRepository
from app.repositories.product_repo import ProductRepository, VariantRepository, CategoryRepository
from app.repositories.retailer_repo import RetailerRepository, RetailerProductRepository
from app.schemas.diagnosis import (
    DiagnosisResultResponse,
    AnalysisInfo,
    DiagnosisTagResponse,
    RecommendedProductResponse,
    RetailerAvailabilityResponse
)
from app.models.diagnosis import DiagnosisCase, GeminiOutput, DiagnosisTag
from app.models.farmer import Farmer


# =============================================================================
# Rule-Based Mapping Configuration
# =============================================================================

# Tag-to-category mapping (config-driven, no AI)
TAG_TO_CATEGORY_MAP: Dict[str, List[str]] = {
    # Urgency levels
    "urgency:critical": ["emergency_medications", "veterinary_supplies"],
    "urgency:high": ["antibiotics", "anti_inflammatory"],
    "urgency:medium": ["supplements", "general_medications"],
    "urgency:low": ["preventive_care", "supplements"],
    
    # Common conditions
    "mastitis": ["antibiotics", "udder_care", "anti_inflammatory"],
    "foot_rot": ["hoof_care", "antibiotics", "antiseptics"],
    "bloat": ["emergency_medications", "digestive_aids"],
    "pneumonia": ["antibiotics", "respiratory_care"],
    "diarrhea": ["electrolytes", "probiotics", "antibiotics"],
    "fever": ["anti_inflammatory", "antipyretics"],
    "skin_lesion": ["antiseptics", "wound_care", "topical_treatments"],
    "parasites": ["dewormers", "antiparasitic"],
    "eye_infection": ["eye_care", "antibiotics"],
    
    # Symptoms
    "swelling": ["anti_inflammatory", "topical_treatments"],
    "lameness": ["hoof_care", "anti_inflammatory"],
    "discharge": ["antibiotics", "antiseptics"],
    "loss_of_appetite": ["digestive_aids", "supplements", "vitamins"],
    "weight_loss": ["supplements", "dewormers", "feed_additives"],
}

# Default categories when no specific match
DEFAULT_CATEGORIES = ["general_medications", "supplements"]


class RecommendationService:
    """
    Service for deterministic product recommendations.
    
    Responsibilities:
    - Read latest GeminiOutput metadata (not raw response via API)
    - Read diagnosis_tags for mapping
    - Map tags to product categories (rule-based)
    - Fetch available products from retailers
    - Compute distance dynamically
    
    No AI logic. No Gemini calls. Rule/config driven only.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.diagnosis_repo = DiagnosisRepository(db)
        self.gemini_output_repo = GeminiOutputRepository(db)
        self.tag_repo = TagRepository(db)
        self.farmer_repo = FarmerRepository(db)
        self.category_repo = CategoryRepository(db)
        self.product_repo = ProductRepository(db)
        self.variant_repo = VariantRepository(db)
        self.retailer_repo = RetailerRepository(db)
        self.retailer_product_repo = RetailerProductRepository(db)
    
    async def get_diagnosis_result(
        self,
        case_id: uuid.UUID,
        farmer_id: uuid.UUID
    ) -> DiagnosisResultResponse:
        """
        Get diagnosis result with product recommendations.
        
        Returns structured data for API consumption.
        Does NOT expose raw Gemini response.
        """
        # Get diagnosis case
        case = await self.diagnosis_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Diagnosis case not found: {case_id}")
        
        if case.farmer_id != farmer_id:
            raise ValueError("Case does not belong to this farmer")
        
        # Get farmer for location
        farmer = await self.farmer_repo.get_by_id(farmer_id)
        
        # Get latest Gemini output (metadata only - no raw response)
        gemini_output = await self.gemini_output_repo.get_latest_by_case(case_id)
        analysis_info = None
        if gemini_output:
            analysis_info = AnalysisInfo(
                id=gemini_output.id,
                model_id=gemini_output.model_id,
                created_at=gemini_output.created_at
            )
        
        # Get diagnosis tags
        tags = await self.tag_repo.get_by_case(case_id)
        tag_responses = [
            DiagnosisTagResponse(tag=t.tag, source=t.source or "unknown")
            for t in tags
        ]
        
        # Get product recommendations using rule-based mapping
        recommended_products = await self._get_recommendations_from_tags(
            tags,
            farmer
        )
        
        # Update status if first time viewing
        if case.status == "analyzed":
            await self.diagnosis_repo.update_status(case_id, "recommendation_shown")
        
        return DiagnosisResultResponse(
            diagnosis_case_id=case_id,
            status=case.status,
            analysis=analysis_info,
            tags=tag_responses,
            recommended_products=recommended_products
        )
    
    async def _get_recommendations_from_tags(
        self,
        tags: List[DiagnosisTag],
        farmer: Optional[Farmer]
    ) -> List[RecommendedProductResponse]:
        """
        Map diagnosis tags to product recommendations.
        
        Uses rule-based TAG_TO_CATEGORY_MAP configuration.
        No AI logic - deterministic mapping only.
        """
        # Extract category keywords from tags using config map
        category_keywords = set()
        
        for tag in tags:
            tag_lower = tag.tag.lower()
            
            # Check direct mapping
            if tag_lower in TAG_TO_CATEGORY_MAP:
                category_keywords.update(TAG_TO_CATEGORY_MAP[tag_lower])
            else:
                # Check partial match
                for key, categories in TAG_TO_CATEGORY_MAP.items():
                    if key in tag_lower or tag_lower in key:
                        category_keywords.update(categories)
        
        # Use defaults if no matches
        if not category_keywords:
            category_keywords = set(DEFAULT_CATEGORIES)
        
        # Search for products matching category keywords
        recommended_products = []
        seen_variants = set()
        
        for keyword in list(category_keywords)[:10]:  # Limit keywords
            products = await self.product_repo.search(
                keyword, 
                active_only=True, 
                limit=5
            )
            
            for product in products:
                variants = await self.variant_repo.get_by_product(
                    product.id, 
                    active_only=True
                )
                
                for variant in variants[:2]:
                    if variant.id in seen_variants:
                        continue
                    seen_variants.add(variant.id)
                    
                    # Get retailer availability
                    retailers = await self._get_retailer_availability(
                        variant.id,
                        farmer
                    )
                    
                    if retailers:
                        recommended_products.append(RecommendedProductResponse(
                            product_variant_id=variant.id,
                            sku=variant.sku,
                            name=variant.name or product.name,
                            retailers=retailers
                        ))
        
        return recommended_products[:10]  # Limit total recommendations
    
    async def _get_retailer_availability(
        self,
        variant_id: uuid.UUID,
        farmer: Optional[Farmer]
    ) -> List[RetailerAvailabilityResponse]:
        """
        Get retailers stocking a product variant.
        
        Computes distance_km dynamically server-side.
        """
        retailer_products = await self.retailer_product_repo.get_by_variant(
            variant_id,
            available_only=True
        )
        
        availability_list = []
        
        for rp in retailer_products:
            retailer = await self.retailer_repo.get_by_id(rp.retailer_id)
            if not retailer or not retailer.is_active:
                continue
            
            # Compute distance dynamically
            distance_km = self._compute_distance_km(farmer, retailer)
            
            availability_list.append(RetailerAvailabilityResponse(
                retailer_id=retailer.id,
                retailer_name=retailer.name,
                price=rp.price,
                distance_km=distance_km,
                is_available=rp.is_available and rp.stock_quantity > 0
            ))
        
        # Sort by distance
        availability_list.sort(key=lambda x: x.distance_km)
        
        return availability_list[:5]  # Return nearest 5
    
    def _compute_distance_km(
        self,
        farmer: Optional[Farmer],
        retailer
    ) -> float:
        """
        Compute distance between farmer and retailer using Haversine formula.
        
        Computed dynamically server-side per API contract.
        """
        if not farmer or not retailer:
            return 0.0
        
        if not farmer.location_lat or not farmer.location_lng:
            return 0.0
        
        if not retailer.location_lat or not retailer.location_lng:
            return 0.0
        
        lat1 = float(farmer.location_lat)
        lon1 = float(farmer.location_lng)
        lat2 = float(retailer.location_lat)
        lon2 = float(retailer.location_lng)
        
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return round(R * c, 1)
