"""Initial schema v1

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-01-02

Implements the frozen v1 database schema with all 13 tables:
- farmers, animals
- diagnosis_cases, diagnosis_media, gemini_outputs, diagnosis_outcomes, diagnosis_tags
- product_categories, products, product_variants
- retailers, retailer_products
- orders, order_items
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # FARMER DOMAIN
    # ==========================================================================
    
    # farmers table
    op.create_table(
        'farmers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False, unique=True),
        sa.Column('location_lat', sa.Numeric(10, 8), nullable=True),
        sa.Column('location_lng', sa.Numeric(11, 8), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
    )
    op.create_index('ix_farmers_phone', 'farmers', ['phone'])
    
    # animals table
    op.create_table(
        'animals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('farmers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tag_number', sa.String(100), nullable=True),
        sa.Column('species', sa.String(50), nullable=True),
        sa.Column('breed', sa.String(100), nullable=True),
        sa.Column('birth_date', sa.Date, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
    )
    op.create_index('ix_animals_farmer_id', 'animals', ['farmer_id'])
    
    # ==========================================================================
    # DIAGNOSIS DOMAIN
    # ==========================================================================
    
    # diagnosis_cases table
    op.create_table(
        'diagnosis_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('farmers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('animal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('animals.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='created'),
        sa.Column('symptoms_reported', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
    )
    op.create_index('ix_diagnosis_cases_farmer_id', 'diagnosis_cases', ['farmer_id'])
    op.create_index('ix_diagnosis_cases_status', 'diagnosis_cases', ['status'])
    
    # diagnosis_media table
    op.create_table(
        'diagnosis_media',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('diagnosis_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('diagnosis_cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('media_type', sa.String(20), nullable=False),
        sa.Column('storage_path', sa.String(500), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger, nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('captured_at', sa.TIMESTAMP, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_diagnosis_media_case_id', 'diagnosis_media', ['diagnosis_case_id'])
    
    # gemini_outputs table
    op.create_table(
        'gemini_outputs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('diagnosis_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('diagnosis_cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('raw_request', postgresql.JSONB, nullable=True),
        sa.Column('raw_response', postgresql.JSONB, nullable=True),
        sa.Column('model_id', sa.String(100), nullable=True),
        sa.Column('prompt_version', sa.String(50), nullable=True),
        sa.Column('context_version', sa.String(50), nullable=True),
        sa.Column('latency_ms', sa.Integer, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_gemini_outputs_case_id', 'gemini_outputs', ['diagnosis_case_id'])
    
    # diagnosis_outcomes table
    op.create_table(
        'diagnosis_outcomes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('diagnosis_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('diagnosis_cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('farmer_feedback', sa.Text, nullable=True),
        sa.Column('actual_disease', sa.String(255), nullable=True),
        sa.Column('treatment_applied', sa.Text, nullable=True),
        sa.Column('outcome_status', sa.String(50), nullable=True),
        sa.Column('outcome_date', sa.Date, nullable=True),
        sa.Column('reported_at', sa.TIMESTAMP, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_diagnosis_outcomes_case_id', 'diagnosis_outcomes', ['diagnosis_case_id'])
    
    # diagnosis_tags table
    op.create_table(
        'diagnosis_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('diagnosis_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('diagnosis_cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tag', sa.String(100), nullable=False),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_diagnosis_tags_case_id', 'diagnosis_tags', ['diagnosis_case_id'])
    op.create_index('ix_diagnosis_tags_tag', 'diagnosis_tags', ['tag'])
    
    # ==========================================================================
    # PRODUCT CATALOG DOMAIN
    # ==========================================================================
    
    # product_categories table
    op.create_table(
        'product_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('product_categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )
    
    # products table
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('product_categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('manufacturer', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
    )
    op.create_index('ix_products_category_id', 'products', ['category_id'])
    op.create_index('ix_products_is_active', 'products', ['is_active'])
    
    # product_variants table
    op.create_table(
        'product_variants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sku', sa.String(100), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('unit_size', sa.String(50), nullable=True),
        sa.Column('unit_type', sa.String(50), nullable=True),
        sa.Column('base_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
    )
    op.create_index('ix_product_variants_product_id', 'product_variants', ['product_id'])
    op.create_index('ix_product_variants_sku', 'product_variants', ['sku'])
    
    # ==========================================================================
    # RETAILER DOMAIN
    # ==========================================================================
    
    # retailers table
    op.create_table(
        'retailers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('location_lat', sa.Numeric(10, 8), nullable=True),
        sa.Column('location_lng', sa.Numeric(11, 8), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
    )
    op.create_index('ix_retailers_is_active', 'retailers', ['is_active'])
    
    # retailer_products table
    op.create_table(
        'retailer_products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('retailer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('retailers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_variant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('product_variants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('price', sa.Numeric(12, 2), nullable=False),
        sa.Column('stock_quantity', sa.Integer, server_default='0', nullable=False),
        sa.Column('is_available', sa.Boolean, server_default='true', nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
        sa.UniqueConstraint('retailer_id', 'product_variant_id', name='uq_retailer_product_variant'),
    )
    op.create_index('ix_retailer_products_retailer_id', 'retailer_products', ['retailer_id'])
    op.create_index('ix_retailer_products_variant_id', 'retailer_products', ['product_variant_id'])
    
    # ==========================================================================
    # ORDER DOMAIN
    # ==========================================================================
    
    # orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('farmers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('retailer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('retailers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('diagnosis_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('diagnosis_cases.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('source_ref_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('total_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('delivery_address', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True),
    )
    op.create_index('ix_orders_farmer_id', 'orders', ['farmer_id'])
    op.create_index('ix_orders_retailer_id', 'orders', ['retailer_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    
    # order_items table
    op.create_table(
        'order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_variant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('product_variants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'])


def downgrade() -> None:
    # Drop tables in reverse order of creation (respecting foreign keys)
    
    # Order domain
    op.drop_index('ix_order_items_order_id', table_name='order_items')
    op.drop_table('order_items')
    
    op.drop_index('ix_orders_status', table_name='orders')
    op.drop_index('ix_orders_retailer_id', table_name='orders')
    op.drop_index('ix_orders_farmer_id', table_name='orders')
    op.drop_table('orders')
    
    # Retailer domain
    op.drop_index('ix_retailer_products_variant_id', table_name='retailer_products')
    op.drop_index('ix_retailer_products_retailer_id', table_name='retailer_products')
    op.drop_table('retailer_products')
    
    op.drop_index('ix_retailers_is_active', table_name='retailers')
    op.drop_table('retailers')
    
    # Product catalog domain
    op.drop_index('ix_product_variants_sku', table_name='product_variants')
    op.drop_index('ix_product_variants_product_id', table_name='product_variants')
    op.drop_table('product_variants')
    
    op.drop_index('ix_products_is_active', table_name='products')
    op.drop_index('ix_products_category_id', table_name='products')
    op.drop_table('products')
    
    op.drop_table('product_categories')
    
    # Diagnosis domain
    op.drop_index('ix_diagnosis_tags_tag', table_name='diagnosis_tags')
    op.drop_index('ix_diagnosis_tags_case_id', table_name='diagnosis_tags')
    op.drop_table('diagnosis_tags')
    
    op.drop_index('ix_diagnosis_outcomes_case_id', table_name='diagnosis_outcomes')
    op.drop_table('diagnosis_outcomes')
    
    op.drop_index('ix_gemini_outputs_case_id', table_name='gemini_outputs')
    op.drop_table('gemini_outputs')
    
    op.drop_index('ix_diagnosis_media_case_id', table_name='diagnosis_media')
    op.drop_table('diagnosis_media')
    
    op.drop_index('ix_diagnosis_cases_status', table_name='diagnosis_cases')
    op.drop_index('ix_diagnosis_cases_farmer_id', table_name='diagnosis_cases')
    op.drop_table('diagnosis_cases')
    
    # Farmer domain
    op.drop_index('ix_animals_farmer_id', table_name='animals')
    op.drop_table('animals')
    
    op.drop_index('ix_farmers_phone', table_name='farmers')
    op.drop_table('farmers')
