// PatchFilter - Collapsible checkbox tree for filtering runs by game version.
//
// The patch taxonomy (from GET /api/analytics/distinct-versions) is a newest-
// first list of nodes, each { version, tag, children: [{ version, tag }] }. A
// node with a non-empty `children` list is a "release group" that incorporated
// those beta versions; a node with no children is a standalone leaf.
//
// SELECTION MODEL
// ---------------
// The parent is treated as a child of ITSELF: when rendering a group we prepend
// the parent's own { version, tag } as the first child. So a group's selectable
// set is [parent-self, ...incorporated betas].
//   - The group header checkbox toggles the WHOLE subtree (all child rows),
//     showing a tri-state "indeterminate" mark when only some are checked.
//   - To select ONLY the release's own runs, check just the self-row and leave
//     the incorporated betas unchecked.
// Standalone (childless) versions render as a single flat leaf checkbox.
//
// Grouped versions render ONLY inside their group — they do not also get a
// duplicate top-level row (the API returns them at top level too, but those are
// filtered out here so each version appears exactly once).
//
// VALUE SHAPE (persisted + emitted)
// ---------------------------------
// `selection` is either the string 'all' (default — every version selected, the
// fast cache path) or an ARRAY of the explicitly-selected version strings. The
// parent lifts this to a comma-joined `version` query param ('all' stays 'all').

const PatchFilter = ({ tree, selection, onChange }) => {
    const { useState, useMemo, useRef, useEffect } = React;

    const [isOpen, setIsOpen] = useState(false);
    const rootRef = useRef(null);

    // Close the popover on an outside click or Escape, mirroring native <select>.
    useEffect(() => {
        if (!isOpen) return;
        const handlePointerDown = (e) => {
            if (rootRef.current && !rootRef.current.contains(e.target)) {
                setIsOpen(false);
            }
        };
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') setIsOpen(false);
        };
        document.addEventListener('mousedown', handlePointerDown);
        document.addEventListener('keydown', handleKeyDown);
        return () => {
            document.removeEventListener('mousedown', handlePointerDown);
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [isOpen]);

    // The complete set of version strings the tree can select. A grouped version
    // is only counted once (via the group), so we walk top-level leaves plus each
    // group's children (which already include the parent-self row we synthesize).
    const { allVersions, groups, leaves, groupedVersions } = useMemo(() => {
        const groups = [];
        const leaves = [];
        const groupedVersions = new Set();

        for (const node of tree) {
            if (node.children && node.children.length > 0) {
                // Prepend the parent as a child of itself (its own to-main runs).
                const selfRow = { version: node.version, tag: node.tag };
                const rows = [selfRow, ...node.children];
                groups.push({ version: node.version, tag: node.tag, rows });
                rows.forEach(row => groupedVersions.add(row.version));
            }
        }
        // A node is a standalone leaf only if it isn't already inside a group.
        for (const node of tree) {
            const isGroupHeader = node.children && node.children.length > 0;
            if (!isGroupHeader && !groupedVersions.has(node.version)) {
                leaves.push({ version: node.version, tag: node.tag });
            }
        }

        const allVersions = [];
        const seen = new Set();
        const remember = (v) => { if (!seen.has(v)) { seen.add(v); allVersions.push(v); } };
        leaves.forEach(leaf => remember(leaf.version));
        groups.forEach(group => group.rows.forEach(row => remember(row.version)));

        return { allVersions, groups, leaves, groupedVersions };
    }, [tree]);

    // Resolve `selection` ('all' | string[]) to a concrete Set of checked
    // versions. 'all' means every selectable version is checked.
    const checkedSet = useMemo(() => {
        if (selection === 'all') return new Set(allVersions);
        return new Set(selection);
    }, [selection, allVersions]);

    // Emit the next selection, collapsing "everything checked" back to the 'all'
    // sentinel so the fast cache path is preserved and persistence stays compact.
    const emit = (nextChecked) => {
        if (nextChecked.size === allVersions.length) {
            onChange('all');
        } else {
            // Preserve tree order for a stable, readable query param.
            onChange(allVersions.filter(v => nextChecked.has(v)));
        }
    };

    const toggleVersion = (version) => {
        const next = new Set(checkedSet);
        if (next.has(version)) next.delete(version);
        else next.add(version);
        emit(next);
    };

    const toggleGroup = (group) => {
        const versions = group.rows.map(row => row.version);
        const allChecked = versions.every(v => checkedSet.has(v));
        const next = new Set(checkedSet);
        // If the whole subtree is checked, clear it; otherwise fill it in.
        versions.forEach(v => allChecked ? next.delete(v) : next.add(v));
        emit(next);
    };

    const setAll = (checked) => {
        emit(checked ? new Set(allVersions) : new Set());
    };

    // Group tri-state: 'checked' (all), 'empty' (none), or 'partial' (some).
    const groupState = (group) => {
        const versions = group.rows.map(row => row.version);
        const checkedCount = versions.filter(v => checkedSet.has(v)).length;
        if (checkedCount === 0) return 'empty';
        if (checkedCount === versions.length) return 'checked';
        return 'partial';
    };

    // Trigger-button summary: "All Patches", a single version, or "N patches".
    const summaryLabel = useMemo(() => {
        if (selection === 'all' || checkedSet.size === allVersions.length) {
            return 'All Patches';
        }
        if (checkedSet.size === 0) return 'No Patches';
        if (checkedSet.size === 1) return [...checkedSet][0];
        return `${checkedSet.size} patches`;
    }, [selection, checkedSet, allVersions]);

    // A single checkbox row (leaf or child). `indent` nests children under a group.
    const renderCheckboxRow = ({ version, tag }, { indent = false, isSelfRow = false } = {}) =>
        React.createElement('label', {
            key: version,
            className: `patch-row${indent ? ' patch-row--child' : ''}`
        },
            React.createElement('input', {
                type: 'checkbox',
                className: 'patch-checkbox',
                checked: checkedSet.has(version),
                onChange: () => toggleVersion(version)
            }),
            React.createElement('span', { className: 'patch-version' },
                // The self-row labels its own runs so it reads distinctly from
                // the group header that sits directly above it. Kept terse
                // ("(only)") so it doesn't push the tag off-screen.
                isSelfRow ? `${version} (only)` : version
            ),
            tag && React.createElement('span', { className: 'patch-tag' }, tag)
        );

    // A release group: a tri-state header checkbox over its child rows. The first
    // child is the synthesized self-row (the release's own runs).
    const renderGroup = (group) => {
        const state = groupState(group);
        return React.createElement('div', { className: 'patch-group', key: group.version },
            React.createElement('label', { className: 'patch-row patch-row--group' },
                React.createElement('input', {
                    type: 'checkbox',
                    className: 'patch-checkbox',
                    checked: state === 'checked',
                    ref: (el) => { if (el) el.indeterminate = (state === 'partial'); },
                    onChange: () => toggleGroup(group)
                }),
                React.createElement('span', { className: 'patch-version' }, group.version),
                group.tag && React.createElement('span', { className: 'patch-tag' }, group.tag)
            ),
            React.createElement('div', { className: 'patch-group-children' },
                group.rows.map((row, index) =>
                    renderCheckboxRow(row, { indent: true, isSelfRow: index === 0 })
                )
            )
        );
    };

    return React.createElement('div', {
        className: 'filter-group patch-filter',
        ref: rootRef
    },
        React.createElement('label', { className: 'filter-label' }, 'Patch'),
        React.createElement('button', {
            type: 'button',
            className: 'filter-select patch-filter-trigger',
            onClick: () => setIsOpen(prev => !prev)
        },
            React.createElement('span', null, summaryLabel),
            React.createElement('span', { className: 'patch-filter-caret' }, isOpen ? '▴' : '▾')
        ),
        isOpen && React.createElement('div', { className: 'patch-filter-panel' },
            React.createElement('div', { className: 'patch-filter-actions' },
                React.createElement('button', {
                    type: 'button',
                    className: 'patch-filter-action',
                    onClick: () => setAll(true)
                }, 'Select all'),
                React.createElement('button', {
                    type: 'button',
                    className: 'patch-filter-action',
                    onClick: () => setAll(false)
                }, 'Deselect all')
            ),
            React.createElement('div', { className: 'patch-filter-tree' },
                // Interleave leaves and groups in the tree's newest-first order.
                // Leaves and groups were split for logic; re-walk `tree` to render
                // them in their original order.
                tree
                    .filter(node => {
                        const isGroup = node.children && node.children.length > 0;
                        return isGroup || !groupedVersions.has(node.version);
                    })
                    .map(node => {
                        const isGroup = node.children && node.children.length > 0;
                        if (isGroup) {
                            const selfRow = { version: node.version, tag: node.tag };
                            const rows = [selfRow, ...node.children];
                            return renderGroup({ version: node.version, tag: node.tag, rows });
                        }
                        return renderCheckboxRow(node);
                    })
            )
        )
    );
};

// Export component
window.PatchFilter = PatchFilter;
