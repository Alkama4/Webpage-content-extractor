const readOnlyEnv = import.meta.env.VITE_READ_ONLY_MODE?.toLowerCase();
export const READ_ONLY_MODE = readOnlyEnv === "true";
