// InfoIcon - Displays a hoverable info icon with tooltip
const InfoIcon = ({ term }) => {
    const [showTooltip, setShowTooltip] = React.useState(false);
    const glossary = window.Glossary || {};
    const entry = glossary[term];

    if (!entry || !entry.short) {
        return null; // Don't show icon if no description
    }

    return React.createElement('span', {
        className: 'info-icon-wrapper',
        onMouseEnter: () => setShowTooltip(true),
        onMouseLeave: () => setShowTooltip(false),
        style: { position: 'relative', display: 'inline-block', marginLeft: '6px' }
    },
        // Info icon
        React.createElement('span', {
            className: 'info-icon',
            style: {
                display: 'inline-block',
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                backgroundColor: '#3b82f6',
                color: 'white',
                fontSize: '11px',
                fontWeight: 'bold',
                textAlign: 'center',
                lineHeight: '16px',
                cursor: 'help',
                userSelect: 'none',
                textTransform: 'none'
            }
        }, 'i'),

        // Tooltip
        showTooltip && React.createElement('div', {
            className: 'info-tooltip',
            style: {
                position: 'absolute',
                bottom: '100%',
                left: '50%',
                transform: 'translateX(-50%)',
                marginBottom: '8px',
                padding: '10px 12px',
                backgroundColor: '#1f2937',
                color: 'white',
                borderRadius: '6px',
                fontSize: '13px',
                lineHeight: '1.5',
                maxWidth: '300px',
                width: 'max-content',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                zIndex: 1000,
                pointerEvents: 'none',
                whiteSpace: 'normal',
                textTransform: 'none'
            }
        },
            React.createElement('div', { style: { fontWeight: '600', marginBottom: '4px', textTransform: 'none' } }, entry.title),
            React.createElement('div', { style: { textTransform: 'none' } }, entry.short),
            // Arrow
            React.createElement('div', {
                style: {
                    position: 'absolute',
                    top: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: 0,
                    height: 0,
                    borderLeft: '6px solid transparent',
                    borderRight: '6px solid transparent',
                    borderTop: '6px solid #1f2937'
                }
            })
        )
    );
};

// Export component
window.InfoIcon = InfoIcon;
