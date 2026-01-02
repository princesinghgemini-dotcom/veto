interface StatusBadgeProps {
    status: boolean | string;
    activeText?: string;
    inactiveText?: string;
}

export function StatusBadge({
    status,
    activeText = 'Active',
    inactiveText = 'Inactive',
}: StatusBadgeProps) {
    const isActive = typeof status === 'boolean' ? status : status === 'active';

    return (
        <span className={`status-badge ${isActive ? 'active' : 'inactive'}`}>
            {isActive ? activeText : inactiveText}
        </span>
    );
}
