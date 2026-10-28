/**
 * Převede mini-syntaxi z content/*.ts na HTML.
 *   **text** → tučně, [text](url) → odkaz
 * Vstup je escapovaný, takže v textech nemůže skončit nechtěné HTML.
 */
const escape = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** Jednopísmenné předložky a spojky se nesmí ocitnout na konci řádku. */
export const nbsp = (s: string) => s.replace(/(?<=^|[\s(„])([vkszaiouVKSZAIOU]) +/g, '$1\u00a0');

export function rich(input: string): string {
  return nbsp(escape(input))
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(.+?)\]\(([^)\s]+)\)/g, '<a href="$2" class="link">$1</a>')
    .replace(/(?<![\w-])(e-book\w*)/gi, '<span class="whitespace-nowrap">$1</span>');
}

/** Čistý text bez mini-syntaxe (pro meta tagy, aria-label…). */
export function plain(input: string): string {
  return input
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\[(.+?)\]\([^)]+\)/g, '$1');
}
