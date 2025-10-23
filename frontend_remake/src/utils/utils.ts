export function getCssVar(name: string): string {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(name)
        .trim();
}

export function formatTimestamp(time: string): string {
    return new Date(time).toLocaleString("fi-FI", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });
}

export function formatScheduleTime(raw: string | number): string {
    let date = new Date();

    if (typeof raw === "string") {           // "HH:mm"
        const [h = 0, m = 0] = raw.split(":").map(Number);
        date.setHours(h, m);
    } else {                                 // minutes since midnight
        const h = Math.floor(raw / 60);
        const m = raw % 60;
        date.setHours(h, m);
    }

    return date.toLocaleTimeString("fi-FI", { hour: "numeric", minute: "numeric" });
}

// Convert "HH.MM.SS" → "HH:MM[:SS]" (omit seconds if they’re 00)
export function toInputTime(backendStr?: string): Date | string {
    if (!backendStr) return 'null';
    const [h, m, s] = backendStr.split(':').map(Number);
    const base = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    return s && s !== 0 ? `${base}:${String(s).padStart(2, '0')}` : base;
}

// Convert "HH:MM[:SS]" → "HH.MM.SS" (seconds default to 00)
export function toBackendTime(inputStr?: string): string {
    if (!inputStr) return '';
    const parts = inputStr.split(':').map(Number);
    const [h, m, s] = [parts[0], parts[1], parts[2] ?? 0];
    return `${String(h).padStart(2, '0')}.${String(m).padStart(2, '0')}.${String(s).padStart(2, '0')}`;
}