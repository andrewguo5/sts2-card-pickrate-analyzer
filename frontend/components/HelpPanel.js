// HelpPanel - Collapsible help section with full glossary
const HelpPanel = () => {
    const [isOpen, setIsOpen] = React.useState(false);
    const glossary = window.Glossary || {};

    return React.createElement('div', {
        className: 'help-panel',
        style: {
            backgroundColor: '#f9fafb',
            borderBottom: '1px solid #e5e7eb',
            overflow: 'hidden'
        }
    },
        // Toggle button
        React.createElement('button', {
            onClick: () => setIsOpen(!isOpen),
            style: {
                width: '100%',
                padding: '12px 30px',
                backgroundColor: '#f3f4f6',
                border: 'none',
                borderBottom: '1px solid #e5e7eb',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                transition: 'background-color 0.2s'
            },
            onMouseEnter: (e) => e.currentTarget.style.backgroundColor = '#e5e7eb',
            onMouseLeave: (e) => e.currentTarget.style.backgroundColor = '#f3f4f6'
        },
            React.createElement('span', null, '❓ Help & Glossary'),
            React.createElement('span', { style: { fontSize: '12px' } }, isOpen ? '▲ Hide' : '▼ Show')
        ),

        // Content (only shown when open)
        isOpen && React.createElement('div', {
            style: {
                padding: '20px 30px',
                maxHeight: '400px',
                overflowY: 'auto'
            }
        },
            React.createElement('h3', {
                style: {
                    fontSize: '16px',
                    fontWeight: '700',
                    color: '#1f2937',
                    marginBottom: '16px'
                }
            }, 'Analytics Glossary'),

            // Render all glossary entries
            React.createElement('div', {
                style: {
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '20px'
                }
            },
                Object.entries(glossary).map(([key, entry]) =>
                    React.createElement('div', {
                        key: key,
                        style: {
                            backgroundColor: 'white',
                            padding: '14px',
                            borderRadius: '8px',
                            border: '1px solid #e5e7eb'
                        }
                    },
                        React.createElement('div', {
                            style: {
                                fontSize: '14px',
                                fontWeight: '700',
                                color: '#1f2937',
                                marginBottom: '6px'
                            }
                        }, entry.title),
                        React.createElement('div', {
                            style: {
                                fontSize: '13px',
                                lineHeight: '1.6',
                                color: '#4b5563',
                                whiteSpace: 'pre-line'
                            }
                        }, entry.full)
                    )
                )
            )
        )
    );
};

// Export component
window.HelpPanel = HelpPanel;
