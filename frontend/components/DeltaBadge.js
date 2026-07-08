// DeltaBadge - Inline trend indicator showing how the most recent runs shifted a
// stat away from its baseline. Rendered next to a headline stat value.
//
// Props:
//   deltaPp     - signed percentage-point difference (headline - baseline)
//   sufficient  - whether the recent window had enough samples to trust the delta
//
// States:
//   insufficient / exactly flat -> muted grey dash (no misleading arrow)
//   positive delta              -> green up arrow + "+X.X pp"
//   negative delta              -> red down arrow + "X.X pp"
const DeltaBadge = ({ deltaPp, sufficient }) => {
    const baseStyle = {
        display: 'inline-block',
        marginLeft: '8px',
        fontSize: '13px',
        fontWeight: 600,
        textTransform: 'none',
        verticalAlign: 'middle'
    };

    if (!sufficient || deltaPp === 0) {
        return React.createElement('span', {
            style: { ...baseStyle, color: '#9ca3af' },
            title: sufficient ? 'No change from recent runs' : 'Not enough recent runs'
        }, '–'); // en dash
    }

    const isUp = deltaPp > 0;
    const arrow = isUp ? '▲' : '▼'; // ▲ / ▼ (arrow conveys direction; magnitude is unsigned)
    const color = isUp ? 'var(--trend-up)' : 'var(--trend-down)';

    return React.createElement('span', {
        style: { ...baseStyle, color },
        title: 'Change from the most recent runs vs. earlier baseline'
    }, `${arrow} ${Math.abs(deltaPp).toFixed(1)} pp`);
};

// Export component
window.DeltaBadge = DeltaBadge;
