// FilterBar - Filter controls for character, mode, ascension, and user selection
const FilterBar = ({
    selectedCharacter,
    setSelectedCharacter,
    selectedMode,
    setSelectedMode,
    selectedAscension,
    setSelectedAscension,
    selectedUser,
    setSelectedUser,
    usersList,
    usernameCache,
    filteredRunCounts,
    onOpenGlossary,
    viewMode,
    setViewMode
}) => {
    const { CHARACTERS, MODES, ASCENSIONS } = window.AppConfig;

    return React.createElement('div', { className: 'filters' },
        // Character filter
        React.createElement('div', { className: 'filter-group' },
            React.createElement('label', { className: 'filter-label' }, 'Character'),
            React.createElement('select', {
                className: 'filter-select',
                value: selectedCharacter,
                onChange: (e) => setSelectedCharacter(e.target.value)
            },
                CHARACTERS.map(char =>
                    React.createElement('option', {
                        key: char.id,
                        value: char.id
                    }, char.name)
                )
            )
        ),

        // Mode filter
        React.createElement('div', { className: 'filter-group' },
            React.createElement('label', { className: 'filter-label' }, 'Mode'),
            React.createElement('select', {
                className: 'filter-select',
                value: selectedMode,
                onChange: (e) => setSelectedMode(e.target.value)
            },
                MODES.map(mode =>
                    React.createElement('option', {
                        key: mode.id,
                        value: mode.id
                    }, mode.name)
                )
            )
        ),

        // Ascension filter
        React.createElement('div', { className: 'filter-group' },
            React.createElement('label', { className: 'filter-label' }, 'Ascension'),
            React.createElement('select', {
                className: 'filter-select',
                value: selectedAscension,
                onChange: (e) => setSelectedAscension(e.target.value)
            },
                ASCENSIONS.map(asc =>
                    React.createElement('option', {
                        key: asc.id,
                        value: asc.id
                    }, asc.name)
                )
            )
        ),

        // User filter
        React.createElement('div', { className: 'filter-group' },
            React.createElement('label', { className: 'filter-label' }, 'User'),
            React.createElement('select', {
                className: 'filter-select',
                value: selectedUser || '',
                onChange: (e) => setSelectedUser(e.target.value || null)
            },
                React.createElement('option', { value: '' }, 'Global Stats (All Users)'),
                usersList.map(user => {
                    const username = usernameCache[user.steam_id] || user.steam_id;

                    // If filteredRunCounts is loaded (object exists), show filtered count
                    // If user not in filteredRunCounts, they have 0 runs matching filters
                    const hasLoadedFilteredCounts = Object.keys(filteredRunCounts).length > 0;
                    const filteredCount = filteredRunCounts[user.steam_id] || 0;

                    const displayText = hasLoadedFilteredCounts
                        ? `${username} (${filteredCount} runs, ${user.run_count} total)`
                        : `${username} (${user.run_count} runs)`;

                    return React.createElement('option', {
                        key: user.steam_id,
                        value: user.steam_id
                    }, displayText);
                })
            )
        ),

        // View mode toggle (binary slider)
        React.createElement('div', {
            className: 'filter-group',
            style: { marginLeft: '20px' }
        },
            React.createElement('label', { className: 'filter-label' }, 'View'),
            React.createElement('div', {
                className: 'view-toggle',
                style: {
                    position: 'relative',
                    width: '140px',
                    height: '36px',
                    backgroundColor: '#374151',
                    borderRadius: '18px',
                    border: '2px solid #4b5563',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    padding: '2px'
                },
                onClick: () => setViewMode(viewMode === 'table' ? 'visualization' : 'table')
            },
                // Slider background with labels
                React.createElement('div', {
                    style: {
                        display: 'flex',
                        width: '100%',
                        height: '100%',
                        position: 'relative',
                        zIndex: 1
                    }
                },
                    React.createElement('div', {
                        style: {
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '12px',
                            fontWeight: '600',
                            color: viewMode === 'table' ? '#1f2937' : '#d1d5db',
                            transition: 'color 0.3s',
                            position: 'relative',
                            zIndex: 2
                        }
                    }, 'Table'),
                    React.createElement('div', {
                        style: {
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '12px',
                            fontWeight: '600',
                            color: viewMode === 'visualization' ? '#1f2937' : '#d1d5db',
                            transition: 'color 0.3s',
                            position: 'relative',
                            zIndex: 2
                        }
                    }, 'Chart')
                ),
                // Sliding button
                React.createElement('div', {
                    style: {
                        position: 'absolute',
                        top: '2px',
                        left: viewMode === 'table' ? '2px' : 'calc(50%)',
                        width: 'calc(50% - 2px)',
                        height: 'calc(100% - 4px)',
                        backgroundColor: 'white',
                        borderRadius: '16px',
                        transition: 'left 0.3s ease',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                    }
                })
            )
        ),

        // Glossary button (on the right)
        React.createElement('button', {
            className: 'glossary-button',
            onClick: onOpenGlossary,
            style: {
                marginLeft: 'auto',
                padding: '8px 16px',
                backgroundColor: '#374151',
                color: 'white',
                border: '2px solid #4b5563',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.2s'
            },
            onMouseEnter: (e) => {
                e.currentTarget.style.backgroundColor = '#4b5563';
                e.currentTarget.style.borderColor = '#6b7280';
            },
            onMouseLeave: (e) => {
                e.currentTarget.style.backgroundColor = '#374151';
                e.currentTarget.style.borderColor = '#4b5563';
            }
        },
            React.createElement('span', { style: { fontSize: '16px' } }, '?'),
            React.createElement('span', null, 'Glossary')
        )
    );
};

// Export component
window.FilterBar = FilterBar;
