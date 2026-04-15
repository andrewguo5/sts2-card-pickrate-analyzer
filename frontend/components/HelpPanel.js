// HelpPanel - Slide-out glossary panel from the right
const HelpPanel = ({ isOpen, onClose }) => {
    const glossary = window.Glossary || {};

    // Don't render anything if not open
    if (!isOpen) return null;

    return React.createElement(React.Fragment, null,
        // Backdrop overlay
        React.createElement('div', {
            style: {
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                zIndex: 1000,
                animation: 'fadeIn 0.2s'
            },
            onClick: onClose
        }),

        // Side panel
        React.createElement('div', {
            className: 'glossary-panel',
            style: {
                position: 'fixed',
                top: 0,
                right: 0,
                width: '500px',
                maxWidth: '90vw',
                height: '100vh',
                backgroundColor: 'white',
                boxShadow: '-4px 0 12px rgba(0, 0, 0, 0.15)',
                zIndex: 1001,
                display: 'flex',
                flexDirection: 'column',
                animation: 'slideInRight 0.3s'
            }
        },
            // Header
            React.createElement('div', {
                style: {
                    padding: '20px 24px',
                    borderBottom: '2px solid #e5e7eb',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    backgroundColor: '#f9fafb'
                }
            },
                React.createElement('h2', {
                    style: {
                        fontSize: '20px',
                        fontWeight: '700',
                        color: '#1f2937',
                        margin: 0
                    }
                }, '📖 Glossary'),
                React.createElement('button', {
                    onClick: onClose,
                    style: {
                        width: '32px',
                        height: '32px',
                        border: 'none',
                        backgroundColor: '#e5e7eb',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '18px',
                        color: '#374151',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'background-color 0.2s'
                    },
                    onMouseEnter: (e) => e.currentTarget.style.backgroundColor = '#d1d5db',
                    onMouseLeave: (e) => e.currentTarget.style.backgroundColor = '#e5e7eb'
                }, '×')
            ),

            // Content
            React.createElement('div', {
                style: {
                    flex: 1,
                    overflowY: 'auto',
                    padding: '24px'
                }
            },
                Object.entries(glossary).map(([key, entry]) =>
                    React.createElement('div', {
                        key: key,
                        style: {
                            marginBottom: '24px',
                            paddingBottom: '24px',
                            borderBottom: '1px solid #e5e7eb'
                        }
                    },
                        React.createElement('div', {
                            style: {
                                fontSize: '16px',
                                fontWeight: '700',
                                color: '#1f2937',
                                marginBottom: '8px'
                            }
                        }, entry.title),
                        React.createElement('div', {
                            style: {
                                fontSize: '14px',
                                lineHeight: '1.7',
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
