import { wait } from '@/utils';

let initialized = false;
let go: Go;
let goExitPromise: Promise<void> | undefined;

const CACHE_KEY = 'openim-wasm-cache';

export const WASM_INIT_FAILED = 'WASM_INIT_FAILED';

export async function initializeWasm(url: string): Promise<Go | null> {
  if (initialized) {
    return null;
  }

  if (typeof window === 'undefined') {
    return Promise.resolve(null);
  }

  if (!url) {
    throw new Error(`${WASM_INIT_FAILED}: empty wasm url`);
  }

  const nextGo = new Go();
  try {
    const wasm = await instantiate(url, nextGo);
    nextGo.run(wasm.instance);
  } catch (error) {
    console.error('Failed to initialize WASM:', error);
    throw new Error(
      `${WASM_INIT_FAILED}: ${(error as Error)?.message ?? error}`
    );
  }

  go = nextGo;
  await wait(100);
  initialized = true;
  return go;
}

async function instantiate(url: string, target: Go) {
  if (!('instantiateStreaming' in WebAssembly)) {
    const bytes = await fetchWithCache(url).then(resp => resp.arrayBuffer());
    return WebAssembly.instantiate(bytes, target.importObject);
  }
  try {
    return await WebAssembly.instantiateStreaming(
      fetchWithCache(url),
      target.importObject
    );
  } catch (error) {
    // A wrong Content-Type makes streaming reject; retry from raw bytes.
    const bytes = await fetchWithCache(url).then(resp => resp.arrayBuffer());
    return WebAssembly.instantiate(bytes, target.importObject);
  }
}

export function reset() {
  initialized = false;
}

export function isInitialized() {
  return initialized;
}

export function getGO() {
  return go;
}

export function getGoExitPromise() {
  return goExitPromise;
}

async function fetchWithCache(url: string): Promise<Response> {
  if (!('caches' in window)) {
    return fetch(url);
  }

  const isResourceUpdated = async () => {
    const serverResponse = await fetch(url, { method: 'HEAD' });
    const etag = serverResponse.headers.get('ETag');
    const lastModified = serverResponse.headers.get('Last-Modified');
    return (
      serverResponse.ok &&
      (etag !== cachedResponse?.headers.get('ETag') ||
        lastModified !== cachedResponse?.headers.get('Last-Modified'))
    );
  };

  const cache = await caches.open(CACHE_KEY);
  const cachedResponse = await cache.match(url);
  if (cachedResponse && !(await isResourceUpdated())) {
    return cachedResponse;
  }

  return fetchAndUpdateCache(url, cache);
}

async function fetchAndUpdateCache(
  url: string,
  cache: Cache
): Promise<Response> {
  const response = await fetch(url, { cache: 'no-cache' });
  try {
    await cache.put(url, response.clone());
  } catch (error) {
    console.warn('Failed to put cache');
  }
  return response;
}
