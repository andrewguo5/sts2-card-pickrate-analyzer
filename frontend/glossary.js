// Glossary - User-editable explanations for analytics terms
//
// Edit the descriptions below to customize the help text shown to users.
// These will appear as tooltips (hover) and in the help panel.

window.Glossary = {
    // Core Metrics
    "pick_rate": {
        title: "Pick Rate",
        short: "How often this card is picked when offered",
        full: `How often this card is picked when offered. \n
        (# of times picked) / (# of times offered). Excludes shops.`
    },

    "skip_rate": {
        title: "Skip Rate",
        short: "How often the Skip button is clicked when this card is offered",
        full: `How often the Skip button is clicked when this card is offered. \n
        A skip is when none of the cards offered are chosen. If a card is not \n
        picked, it is either skipped or another card is picked instead. This stat \n
        tracks how often the card is skipped as opposed to losing to a better card. \n
        (# of times this card was offered and skipped) / (# of times this card was offered)`
    },

    "baseline_skip_rate": {
        title: "Baseline Skip Rate",
        short: "On average, how often card rewards are skipped on a given floor.",
        full: `On average, how often card rewards are skipped on a given floor, \n
        for a given character/mode/ascension/player. If cards are skipped at a lower \n
        frequency than baseline, then they are picked more often than expected. \n
        (# of times all cards were skipped) / (# of times a card reward was offered)`
    },

    "win_rate": {
        title: "Win Rate",
        short: "How often a deck containing at least one copy of this card wins.",
        full: `How often a deck containing at least one copy of this card wins.\n
        (# of wins with this card in the deck) / (total # of runs with this card in the deck)`

    },

    // Technical Terms
    "kernel_smoothing": {
        title: "Kernel Smoothing",
        short: "Averages the raw stats from the neighboring +/- 2 floors (b=2)",
        full: `Averages the raw stats from the neighboring +/- 2 floors (b=2). \n
        Kernel smoothing uses a sliding window to smooth out sparse data. \n
        The parameter b is the band radius that specifies the width of this window.`
    },

    "offered": {
        title: "Times Offered",
        short: "The number of times a card shows up in a card reward screen.",
        full: "The number of times a card shows up in a card reward screen."
    },

    // Add more terms as needed
    // "your_term": {
    //     title: "Display Name",
    //     short: "Tooltip text",
    //     full: "Full explanation"
    // }
};
