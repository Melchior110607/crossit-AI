import { toNextJsHandler } from "better-auth/next-js";

export const runtime = 'nodejs';

export async function GET(request: Request) {
    const { auth } = await import("@/lib/auth.server");
    const handler = toNextJsHandler(auth.handler);
    return handler.GET(request);
}

export async function POST(request: Request) {
    const { auth } = await import("@/lib/auth.server");
    const handler = toNextJsHandler(auth.handler);
    return handler.POST(request);
}

