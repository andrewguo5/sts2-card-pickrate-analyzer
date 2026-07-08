// DeltaBadge - Inline trend indicator showing how the most recent runs shifted a
// stat away from its baseline. Rendered next to a headline stat value.
//
// Props:
//   deltaPp       - signed percentage-point difference (headline - baseline)
//   sufficient    - whether the recent window had enough samples to trust the delta
//   hideWhenFlat  - if true, render nothing (instead of a grey dash) when the delta
//                   is insufficient or flat; used in the dense sidebar list
//
// States:
//   insufficient / exactly flat -> muted grey dash (or nothing if hideWhenFlat)
//   positive delta              -> green up arrow + "X.X pp"
//   negative delta              -> red down arrow + "X.X pp"
const DeltaBadge = ({ deltaPp, sufficient, hideWhenFlat = false }) => {
    const baseStyle = {
        display: 'inline-block',
        marginLeft: '8px',
        fontSize: '13px',
        fontWeight: 600,
        textTransform: 'none',
        verticalAlign: 'middle'
    };

    if (!sufficient || deltaPp === 0) {
        if (hideWhenFlat) return null;
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
