// FilterPalette - Condensed, icon-based multi-select filters for Type, Rarity,
// and Cost. Shared by the Table (CardList) and Chart (VisualizationTab) views so
// both read the same visual vocabulary. Each dimension is an independent
// multi-select: an EMPTY selection means "show all" for that dimension, so there
// is no explicit "All" control.
//
// The Type glyphs + colors intentionally match the scatter plot's point shapes
// (triangle/square/circle) and colors, so a filter chip and the dot it selects
// read as the same thing.
//
// Props (each selection is an array of the active option values):
//   filterTypes     - subset of ['Attack','Skill','Power']
//   filterRarities  - subset of ['Common','Uncommon','Rare']
//   filterCosts     - subset of ['0','1','2','3+','X']
//   onToggleType / onToggleRarity / onToggleCost - (value) => void, toggles one
//   layout          - 'sidebar' (stacked, default) or 'inline' (wraps in a row)

// Shared option definitions — single source of truth for order, colors, glyphs.
const FILTER_TYPES = [
    { value: 'Attack', color: 'rgba(220,53,69,1)', shape: 'triangle', title: 'Attacks' },
    { value: 'Skill',  color: 'rgba(40,167,69,1)', shape: 'square',   title: 'Skills' },
    { value: 'Power',  color: 'rgba(59,130,246,1)', shape: 'circle',  title: 'Powers' }
];

const FILTER_RARITIES = [
    { value: 'Common',   color: '#f3f4f6' },
    { value: 'Uncommon', color: '#60a5fa' },
    { value: 'Rare',     color: '#d4af37' }
];

const FILTER_COSTS = ['0', '1', '2', '3+', 'X'];

// Gold highlight for the active state of the Type and Cost toggles.
const ACTIVE_GOLD = '#d4af37';

// A small SVG glyph in the given color, matching the scatter's point shapes.
function TypeGlyph({ shape, color }) {
    const fill = { fill: color };
    const body =
        shape === 'triangle' ? React.createElement('polygon', { points: '10,2 18,17 2,17', ...fill }) :
        shape === 'square'   ? React.createElement('rect', { x: 3, y: 3, width: 14, height: 14, rx: 2, ...fill }) :
                               React.createElement('circle', { cx: 10, cy: 10, r: 8, ...fill });
    return React.createElement('svg', {
        viewBox: '0 0 20 20',
        style: { width: '18px', height: '18px', display: 'block' }
    }, body);
}

const FilterPalette = ({
    filterTypes = [],
    filterRarities = [],
    filterCosts = [],
    onToggleType,
    onToggleRarity,
    onToggleCost,
    layout = 'sidebar'
}) => {
    const groupStyle = { marginBottom: '14px' };
    const labelStyle = {
        display: 'block',
        fontSize: '11px',
        fontWeight: '700',
        color: '#9ca3af',
        textTransform: 'uppercase',
        letterSpacing: '0.6px',
        marginBottom: '8px'
    };
    const rowStyle = { display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' };

    // A single square toggle (Type glyph or Cost numeral) — gold border when
    // active, neutral otherwise. Shared so Type and Cost read identically. The
    // active/inactive fill is overridable so Type can carry a light selected
    // tint while Cost keeps its darker chip look.
    const squareToggle = (key, active, onClick, extra, child) => React.createElement('div', {
        key,
        className: `${extra.className}${active ? ' active' : ''}`,
        title: extra.title,
        onClick,
        style: {
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            height: '34px', borderRadius: '8px',
            background: active ? (extra.activeBg || '#0d1526') : (extra.bg || '#1f2937'),
            border: `2px solid ${active ? ACTIVE_GOLD : '#374151'}`,
            cursor: 'pointer', transition: 'all 0.15s',
            ...extra.style
        }
    }, child);

    // --- Type: glyph swatches (triangle/square/circle in scatter colors) ---
    // Glyphs keep their full color regardless of selection; selection adds a gold
    // border plus a light gold tint. Tooltips explain each shape (Attacks, etc.).
    const typeControls = React.createElement('div', { className: 'filter-palette-group filter-palette-type' },
        React.createElement('label', { style: labelStyle }, 'Type'),
        React.createElement('div', { style: rowStyle },
            FILTER_TYPES.map(({ value, color, shape, title }) =>
                squareToggle(
                    value,
                    filterTypes.includes(value),
                    () => onToggleType(value),
                    { className: 'type-toggle', title, activeBg: 'rgba(212,175,55,0.18)', style: { width: '36px' } },
                    React.createElement(TypeGlyph, { shape, color })
                )
            )
        )
    );

    // --- Cost: little square click-boxes (0 1 2 3+ X) ---
    const costControls = React.createElement('div', { className: 'filter-palette-group filter-palette-cost' },
        React.createElement('label', { style: labelStyle }, 'Cost'),
        React.createElement('div', { style: rowStyle },
            FILTER_COSTS.map((value) => {
                const active = filterCosts.includes(value);
                return squareToggle(
                    value,
                    active,
                    () => onToggleCost(value),
                    {
                        className: 'cost-box',
                        style: {
                            // Square boxes — width matches the shared 34px height.
                            width: '34px',
                            fontSize: '14px', fontWeight: '700',
                            color: active ? '#f3f4f6' : '#9ca3af'
                        }
                    },
                    value
                );
            })
        )
    );

    // Type and Cost share one row, split by a subtle vertical divider.
    const divider = React.createElement('div', {
        'aria-hidden': true,
        style: { alignSelf: 'stretch', width: '1px', background: '#374151', margin: '0 2px' }
    });
    const typeCostRow = React.createElement('div', {
        className: 'filter-palette-typecost',
        style: { display: 'flex', alignItems: 'flex-start', gap: '6px', flexWrap: 'wrap', ...groupStyle }
    }, typeControls, divider, costControls);

    // --- Rarity: checkbox + black label, all on one row ---
    // Gold checkboxes when selected; black labels keep the row readable and compact.
    const rarityGroup = React.createElement('div', { className: 'filter-palette-group', style: groupStyle },
        React.createElement('label', { style: labelStyle }, 'Rarity'),
        React.createElement('div', { style: { display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center' } },
            FILTER_RARITIES.map(({ value }) => {
                const active = filterRarities.includes(value);
                return React.createElement('div', {
                    key: value,
                    className: `rarity-opt${active ? ' active' : ''}`,
                    onClick: () => onToggleRarity(value),
                    style: {
                        display: 'flex', alignItems: 'center', gap: '6px',
                        cursor: 'pointer', userSelect: 'none'
                    }
                },
                    // Gold checkbox when checked; the dark checkmark reads on gold.
                    React.createElement('span', {
                        style: {
                            width: '16px', height: '16px', borderRadius: '4px', flex: 'none',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            background: active ? ACTIVE_GOLD : '#111827',
                            border: `2px solid ${active ? ACTIVE_GOLD : '#4b5563'}`,
                            transition: 'all 0.15s'
                        }
                    },
                        active && React.createElement('span', {
                            style: {
                                width: '4px', height: '8px', marginTop: '-2px',
                                border: 'solid #111827', borderWidth: '0 2px 2px 0',
                                transform: 'rotate(45deg)'
                            }
                        })
                    ),
                    // Black label, always — maximizes readability.
                    React.createElement('span', {
                        style: { fontSize: '14px', fontWeight: '600', color: '#111827' }
                    }, value)
                );
            })
        )
    );

    const containerStyle = layout === 'inline'
        ? { display: 'flex', flexWrap: 'wrap', gap: '20px', alignItems: 'flex-start' }
        : {};

    return React.createElement('div', { className: `filter-palette filter-palette-${layout}`, style: containerStyle },
        typeCostRow,
        rarityGroup
    );
};

// Classify a card's numeric cost + is_x_cost flag into one of the Cost filter
// buckets. X-cost cards report a flattened numeric cost, so is_x_cost wins first.
// Costs of 3 or higher (including the occasional 4/5/9) collapse into '3+'.
function costBucket(cost, isXCost) {
    if (isXCost) return 'X';
    if (cost === null || cost === undefined) return null;
    if (cost <= 0) return '0';
    if (cost === 1) return '1';
    if (cost === 2) return '2';
    return '3+';
}

// Add value to the array if absent, remove it if present. Drives the multi-select
// toggles; returns a new array (never mutates the input).
function toggleInArray(array, value) {
    return array.includes(value)
        ? array.filter(item => item !== value)
        : [...array, value];
}

// Export component + shared helpers so both views classify costs and toggle
// selections identically.
window.FilterPalette = FilterPalette;
window.costBucket = costBucket;
window.toggleInArray = toggleInArray;
