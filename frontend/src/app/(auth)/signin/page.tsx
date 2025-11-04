'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { useState } from "react";
import { Loader2, Sparkles, ShoppingBag } from "lucide-react";
import { signIn } from "@/lib/auth-client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export default function SignInPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const router = useRouter();

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-premium p-4 relative overflow-hidden">
            {/* Effet de fond animé */}
            <div className="absolute inset-0 opacity-20">
                <div className="absolute top-20 left-20 w-72 h-72 bg-skyblue/30 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute bottom-20 right-20 w-96 h-96 bg-warmgold/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
            </div>

            <div className="w-full max-w-md relative z-10 animate-fade-in">
                {/* Logo et titre */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-electric shadow-electric mb-4">
                        <ShoppingBag className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-darktext mb-2">
                        Welcome to <span className="text-warmgold">CrossIt</span>
                    </h1>
                    <p className="text-darktext/60 text-sm">
                        Your premium e-commerce cross-listing platform
                    </p>
                </div>

                <Card className="glass-effect shadow-premium border-warmgold/20">
                    <CardHeader className="space-y-1 pb-4">
                        <CardTitle className="text-2xl font-bold text-center text-darktext">
                            Sign In
                        </CardTitle>
                        <CardDescription className="text-center text-darktext/60">
                            Enter your credentials to access your account
                        </CardDescription>
                    </CardHeader>
                    
                    <CardContent className="space-y-4">
                        {/* Email field */}
                        <div className="space-y-2">
                            <Label htmlFor="email" className="text-darktext/90">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="your@email.com"
                                className="bg-lightgray border-warmgold/20 text-darktext placeholder:text-darktext/40 focus:border-skyblue focus:ring-skyblue"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        {/* Password field */}
                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password" className="text-darktext/90">Password</Label>
                                <Link
                                    href="#"
                                    className="text-xs text-skyblue hover:text-skyblue/80 transition-colors"
                                >
                                    Forgot password?
                                </Link>
                            </div>
                            <Input
                                id="password"
                                type="password"
                                placeholder="••••••••"
                                className="bg-lightgray border-warmgold/20 text-darktext placeholder:text-darktext/40 focus:border-skyblue focus:ring-skyblue"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        {/* Remember me */}
                        <div className="flex items-center space-x-2">
                            <Checkbox
                                id="remember"
                                checked={rememberMe}
                                onCheckedChange={(checked) => setRememberMe(checked as boolean)}
                                className="border-warmgold/40 data-[state=checked]:bg-warmgold data-[state=checked]:border-warmgold"
                            />
                            <Label
                                htmlFor="remember"
                                className="text-sm text-darktext/80 cursor-pointer select-none"
                            >
                                Remember me
                            </Label>
                        </div>

                        {/* Sign in button */}
                        <Button
                            className="w-full bg-gradient-electric hover:opacity-90 text-white font-semibold shadow-electric transition-all duration-300 hover:scale-[1.02]"
                            disabled={loading}
                            onClick={async () => {
                                await signIn.email(
                                    { email, password },
                                    {
                                        onRequest: () => setLoading(true),
                                        onResponse: () => setLoading(false),
                                        onSuccess: () => router.push("/dashboard"),
                                        onError: (ctx) => {
                                            toast.error(ctx.error.message || "Login failed");
                                        },
                                    }
                                );
                            }}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="mr-2 h-4 w-4" />
                                    Sign In
                                </>
                            )}
                        </Button>

                        {/* Divider */}
                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <span className="w-full border-t border-gold/20" />
                            </div>
                            <div className="relative flex justify-center text-xs uppercase">
                                <span className="bg-card px-2 text-beige/60">Or continue with</span>
                            </div>
                        </div>

                        {/* Social buttons */}
                        <div className="grid grid-cols-2 gap-3">
                            <Button
                                variant="outline"
                                className="bg-lightgray/50 border-warmgold/20 text-darktext hover:bg-lightgray hover:border-warmgold/40 transition-all"
                                disabled={loading}
                                onClick={async () => {
                                    await signIn.social(
                                        { provider: "google", callbackURL: "/dashboard" },
                                        {
                                            onRequest: () => setLoading(true),
                                            onResponse: () => setLoading(false),
                                        }
                                    );
                                }}
                            >
                                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                                    <path
                                        fill="currentColor"
                                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                    />
                                    <path
                                        fill="currentColor"
                                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                    />
                                    <path
                                        fill="currentColor"
                                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                    />
                                    <path
                                        fill="currentColor"
                                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                    />
                                </svg>
                                Google
                            </Button>

                            <Button
                                variant="outline"
                                className="bg-lightgray/50 border-warmgold/20 text-darktext hover:bg-lightgray hover:border-warmgold/40 transition-all"
                                disabled={loading}
                                onClick={async () => {
                                    await signIn.social(
                                        { provider: "microsoft", callbackURL: "/dashboard" },
                                        {
                                            onRequest: () => setLoading(true),
                                            onResponse: () => setLoading(false),
                                        }
                                    );
                                }}
                            >
                                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                                    <path fill="currentColor" d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zm12.6 0H12.6V0H24v11.4z" />
                                </svg>
                                Microsoft
                            </Button>
                        </div>

                        {/* Sign up link */}
                        <div className="text-center text-sm text-darktext/60 pt-4">
                            Don't have an account?{" "}
                            <Link href="/sign-up" className="text-warmgold hover:text-warmgold/80 font-semibold transition-colors">
                                Sign up
                            </Link>
                        </div>
                    </CardContent>
                </Card>

                {/* Footer */}
                <p className="text-center text-xs text-darktext/40 mt-8">
                    © 2025 CrossIt. Premium cross-listing platform.
                </p>
            </div>
        </div>
    );
}
