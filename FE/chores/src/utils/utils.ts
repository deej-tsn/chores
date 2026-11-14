/** True when the object has no own enumerable keys. */
export function isEmpty(obj: Record<string, unknown>): boolean {
  return Object.keys(obj).length == 0;
}