// app/frontend/lib/auth.ts
export async function authFetch(input: RequestInfo, init: RequestInit = {}) {
  const headers = new Headers(init.headers || {});
  const token =
    typeof window !== "undefined" ? localStorage.getItem("sb-access-token") : null;

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  } else {
    // dev-only: lets API accept a fake user when AUTH_MODE=dev-noverify
    headers.set("x-dev-email", "dev@local.test");
  }

  return fetch(input, { ...init, headers });
}
