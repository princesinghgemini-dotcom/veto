interface Column<T> {
    key: keyof T | string;
    header: string;
    render?: (item: T) => React.ReactNode;
}

interface DataTableProps<T> {
    columns: Column<T>[];
    data: T[];
    loading?: boolean;
    onRowClick?: (item: T) => void;
}

export function DataTable<T extends { id: string }>({
    columns,
    data,
    loading,
    onRowClick,
}: DataTableProps<T>) {
    if (loading) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <div className="data-table">
            <table>
                <thead>
                    <tr>
                        {columns.map((col) => (
                            <th key={col.key.toString()}>{col.header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((item) => (
                        <tr
                            key={item.id}
                            onClick={() => onRowClick?.(item)}
                            style={{ cursor: onRowClick ? 'pointer' : 'default' }}
                        >
                            {columns.map((col) => (
                                <td key={col.key.toString()}>
                                    {col.render
                                        ? col.render(item)
                                        : String((item as Record<string, unknown>)[col.key as string] ?? '')}
                                </td>
                            ))}
                        </tr>
                    ))}
                    {data.length === 0 && (
                        <tr>
                            <td colSpan={columns.length} style={{ textAlign: 'center', color: '#666' }}>
                                No data found
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
