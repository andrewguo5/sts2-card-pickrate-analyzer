// UploaderGuide - Instructions for installing and running the run-history uploader.
//
// Every command here is sourced from the package itself, not from the project
// READMEs: the console script name comes from pyproject.toml [project.scripts]
// and the flags from mbgg_sts2_uploader/cli.py.
//
// Props:
//   onNavigate - (route, characterId?) => void, supplied by the hash router

// Shown to visitors so they can run the uploader without asking for a code.
// The uploader takes this as a typed argument and never stores it, so rotating
// it here only costs existing users a re-prompt. Change it in one place.
const UPLOAD_ACCESS_CODE = 'mb4l_sts2';

const RUN_FILE_LOCATIONS = [
    { os: 'macOS', path: '~/Library/Application Support/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run' },
    { os: 'Windows', path: '%APPDATA%/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run' }
];

const HOW_IT_WORKS_STEPS = [
    'Finds your run files in the Slay the Spire 2 save directory.',
    'Reads your Steam ID from that directory so runs are attributed to you.',
    'Hashes each run file.',
    'Asks the server which of those runs it already has.',
    'Uploads only the runs that are missing.'
];

const TROUBLESHOOTING = [
    {
        problem: 'Could not find Steam ID',
        fix: 'Play at least one game of Slay the Spire 2 so the game creates your save directory.'
    },
    {
        problem: 'No run files found',
        fix: 'Check that the game is installed and that you have completed runs saved.'
    },
    {
        problem: 'Access denied: Invalid access code',
        fix: 'The code changed. Grab the current one from this page.'
    },
    {
        problem: 'Connection refused',
        fix: 'The analytics server is unreachable. Try again shortly.'
    }
];

// A shell command the visitor is meant to run. Click to copy — the commands are
// short but easy to typo, and a typo here reads as "the tool is broken".
const CodeBlock = ({ command }) => {
    const [copied, setCopied] = React.useState(false);

    const copyCommand = () => {
        navigator.clipboard.writeText(command)
            .then(() => {
                setCopied(true);
                setTimeout(() => setCopied(false), 1500);
            })
            .catch(err => console.error('Could not copy command:', err));
    };

    return React.createElement('div', {
        className: 'uploader-code-block',
        onClick: copyCommand,
        title: 'Click to copy'
    },
        React.createElement('code', null, command),
        React.createElement('span', { className: 'uploader-copy-hint' },
            copied ? 'Copied' : 'Copy'
        )
    );
};

const UploaderGuide = ({ onNavigate }) => {
    const renderStep = (number, heading, ...children) => React.createElement('div',
        { className: 'uploader-step', key: number },
        React.createElement('div', { className: 'uploader-step-number' }, number),
        React.createElement('div', { className: 'uploader-step-body' },
            React.createElement('h3', { className: 'uploader-step-heading' }, heading),
            ...children
        )
    );

    return React.createElement('div', { className: 'uploader-guide' },
        React.createElement('div', { className: 'uploader-column' },
        React.createElement('button', {
            className: 'uploader-back-link',
            onClick: () => onNavigate('landing')
        }, '← Back'),

        React.createElement('div', { className: 'uploader-header' },
            React.createElement('h1', { className: 'uploader-title' }, 'Upload your runs'),
            React.createElement('p', { className: 'uploader-intro' },
                'The analytics on this site are built from run histories that players contribute. ' +
                'The uploader reads the run files Slay the Spire 2 already saves on your machine ' +
                'and sends the ones the server does not have yet. It takes about a minute.'
            )
        ),

        // Fast path for the most common visitor: someone who already installed
        // the uploader and just came back to grab the command. The access code
        // is embedded so they can run it without a second step.
        React.createElement('div', { className: 'uploader-quickrun' },
            React.createElement('h2', { className: 'uploader-quickrun-heading' }, 'Already installed? Run this'),
            React.createElement(CodeBlock, { command: `mbgg-sts2-upload --access-code ${UPLOAD_ACCESS_CODE}` }),
            React.createElement('p', { className: 'uploader-quickrun-note' },
                'First time here? Follow the steps below instead.'
            )
        ),

        React.createElement('div', { className: 'uploader-steps' },
            renderStep(1, 'Install the uploader',
                React.createElement('p', { className: 'uploader-text' },
                    'Requires Python 3.8 or newer.'
                ),
                React.createElement(CodeBlock, { command: 'pip install mbgg-sts2-uploader' })
            ),

            renderStep(2, 'Run it',
                React.createElement(CodeBlock, { command: 'mbgg-sts2-upload' }),
                React.createElement('p', { className: 'uploader-text' },
                    'You will be prompted for an access code. Use:'
                ),
                React.createElement('div', { className: 'uploader-access-code' }, UPLOAD_ACCESS_CODE)
            ),

            renderStep(3, 'That’s it',
                React.createElement('p', { className: 'uploader-text' },
                    'Your runs show up in the analytics within a day. Select yourself from the ',
                    React.createElement('em', null, 'User'),
                    ' dropdown in the analyzer to see your own pick rates alongside everyone else’s.'
                )
            )
        ),

        React.createElement('div', { className: 'uploader-section' },
            React.createElement('h2', { className: 'uploader-section-heading' }, 'Try it without uploading'),
            React.createElement('p', { className: 'uploader-text' },
                'To see which runs would be sent without actually sending them:'
            ),
            React.createElement(CodeBlock, { command: 'mbgg-sts2-upload --dry-run' }),
            React.createElement('p', { className: 'uploader-text' },
                'You can also pass the code directly instead of being prompted:'
            ),
            React.createElement(CodeBlock, { command: `mbgg-sts2-upload --access-code ${UPLOAD_ACCESS_CODE}` })
        ),

        React.createElement('div', { className: 'uploader-section' },
            React.createElement('h2', { className: 'uploader-section-heading' }, 'What it does'),
            React.createElement('ol', { className: 'uploader-list' },
                HOW_IT_WORKS_STEPS.map((step, index) =>
                    React.createElement('li', { key: index }, step)
                )
            ),
            React.createElement('p', { className: 'uploader-text' },
                'Only run history is uploaded. Runs already on the server are skipped, ' +
                'so running the uploader twice is harmless.'
            )
        ),

        React.createElement('div', { className: 'uploader-section' },
            React.createElement('h2', { className: 'uploader-section-heading' }, 'Where your runs live'),
            React.createElement('p', { className: 'uploader-text' },
                'The uploader finds these on its own. Listed in case you want to look:'
            ),
            RUN_FILE_LOCATIONS.map(location =>
                React.createElement('div', { className: 'uploader-path-row', key: location.os },
                    React.createElement('div', { className: 'uploader-path-os' }, location.os),
                    React.createElement('code', { className: 'uploader-path' }, location.path)
                )
            )
        ),

        React.createElement('div', { className: 'uploader-section' },
            React.createElement('h2', { className: 'uploader-section-heading' }, 'If something goes wrong'),
            TROUBLESHOOTING.map(item =>
                React.createElement('div', { className: 'uploader-trouble-row', key: item.problem },
                    React.createElement('div', { className: 'uploader-trouble-problem' }, item.problem),
                    React.createElement('div', { className: 'uploader-trouble-fix' }, item.fix)
                )
            )
        )
        )
    );
};

// Export component
window.UploaderGuide = UploaderGuide;
