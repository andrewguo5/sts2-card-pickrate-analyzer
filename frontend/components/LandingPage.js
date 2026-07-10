// LandingPage - Entry point for the site. Replaces the old behaviour of dropping
// visitors straight into the analyzer with a hard-coded character.
//
// Shows what the dataset covers (total runs, total players) and lets the visitor
// choose which character to analyze, rather than assuming one.
//
// Props:
//   onNavigate - (route, characterId?) => void, supplied by the hash router
const LandingPage = ({ onNavigate }) => {
    const { API_BASE_URL, CHARACTERS } = window.AppConfig;

    // null until the totals resolve; stays null if the request fails.
    const [totals, setTotals] = React.useState(null);

    React.useEffect(() => {
        let cancelled = false;

        fetch(`${API_BASE_URL}/api/analytics/users`)
            .then(response => response.json())
            .then(users => {
                if (cancelled) return;
                setTotals({
                    players: users.length,
                    runs: users.reduce((sum, user) => sum + (user.run_count || 0), 0)
                });
            })
            // The totals are decoration. A dead API shouldn't stop someone from
            // reaching the analyzer, so swallow the error and render without them.
            .catch(err => console.error('Error fetching dataset totals:', err));

        return () => { cancelled = true; };
    }, []);

    const renderTotal = (value, label) => React.createElement('div', { className: 'landing-total' },
        React.createElement('div', { className: 'landing-total-value' },
            value === null ? '—' : value.toLocaleString()
        ),
        React.createElement('div', { className: 'landing-total-label' }, label)
    );

    const renderCharacterTile = (character) => React.createElement('button', {
        key: character.id,
        className: 'landing-character-tile',
        style: { background: character.colors.primary },
        onClick: () => onNavigate('analyzer', character.id)
    },
        React.createElement('span', { className: 'landing-character-name' }, character.name)
    );

    return React.createElement('div', { className: 'landing-page' },
        React.createElement('div', { className: 'landing-column' },
        React.createElement('div', { className: 'landing-hero' },
            React.createElement('h1', { className: 'landing-title' }, 'mbgg'),
            React.createElement('p', { className: 'landing-tagline' },
                'Slay the Spire 2 Analytics' 
            )
        ),

        React.createElement('div', { className: 'landing-totals' },
            renderTotal(totals && totals.runs, 'runs analyzed'),
            renderTotal(totals && totals.players, 'players contributing')
        ),

        React.createElement('div', { className: 'landing-section landing-section--band' },
            React.createElement('h2', { className: 'landing-section-heading' }, 'Choose a character'),
            React.createElement('div', { className: 'landing-character-grid' },
                CHARACTERS.map(renderCharacterTile)
            )
        ),

        React.createElement('div', { className: 'landing-footer' },
            React.createElement('p', { className: 'landing-footer-text' },
                ''
            ),
            React.createElement('button', {
                className: 'landing-upload-cta',
                onClick: () => onNavigate('upload')
            }, 'Upload your runs →')
        )
        )
    );
};

// Export component
window.LandingPage = LandingPage;
