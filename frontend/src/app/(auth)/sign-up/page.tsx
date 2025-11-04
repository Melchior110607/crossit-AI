'use client';

import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Loader2, X, Sparkles, ShoppingBag, UserPlus } from "lucide-react";
import { signUp, signIn } from "@/lib/auth-client";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export default function SignUpPage() {
    const [firstName, setFirstName] = useState("");
	const [lastName, setLastName] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [passwordConfirmation, setPasswordConfirmation] = useState("");
	const [image, setImage] = useState<File | null>(null);
	const [imagePreview, setImagePreview] = useState<string | null>(null);
	const router = useRouter();
	const [loading, setLoading] = useState(false);

	const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (file) {
			setImage(file);
			const reader = new FileReader();
			reader.onloadend = () => {
				setImagePreview(reader.result as string);
			};
			reader.readAsDataURL(file);
		}
	};

	return (
		<div className="min-h-screen flex items-center justify-center bg-gradient-premium p-4 py-12 relative overflow-hidden">
			{/* Effet de fond animé */}
			<div className="absolute inset-0 opacity-30">
				<div className="absolute top-10 right-20 w-72 h-72 bg-electric/20 rounded-full blur-3xl animate-pulse"></div>
				<div className="absolute bottom-10 left-20 w-96 h-96 bg-gold/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
			</div>

			<div className="w-full max-w-md relative z-10 animate-fade-in">
				{/* Logo et titre */}
				<div className="text-center mb-8">
					<div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-electric shadow-electric mb-4">
						<ShoppingBag className="w-8 h-8 text-white" />
					</div>
					<h1 className="text-3xl font-bold text-beige mb-2">
						Join <span className="text-gold">CrossIt</span>
					</h1>
					<p className="text-beige/60 text-sm">
						Start your premium cross-listing journey
					</p>
				</div>

				<Card className="glass-effect shadow-premium border-gold/20">
					<CardHeader className="space-y-1 pb-4">
						<CardTitle className="text-2xl font-bold text-center text-beige flex items-center justify-center gap-2">
							<UserPlus className="w-6 h-6 text-gold" />
							Create Account
						</CardTitle>
						<CardDescription className="text-center text-beige/60">
							Fill in your information to get started
						</CardDescription>
					</CardHeader>
					
					<CardContent className="space-y-4">
						{/* Name fields */}
						<div className="grid grid-cols-2 gap-4">
							<div className="space-y-2">
								<Label htmlFor="first-name" className="text-beige/90">First name</Label>
								<Input
									id="first-name"
									placeholder="John"
									className="bg-warmgray border-gold/20 text-beige placeholder:text-beige/40 focus:border-electric focus:ring-electric"
									value={firstName}
									onChange={(e) => setFirstName(e.target.value)}
									required
								/>
							</div>
							<div className="space-y-2">
								<Label htmlFor="last-name" className="text-beige/90">Last name</Label>
								<Input
									id="last-name"
									placeholder="Doe"
									className="bg-warmgray border-gold/20 text-beige placeholder:text-beige/40 focus:border-electric focus:ring-electric"
									value={lastName}
									onChange={(e) => setLastName(e.target.value)}
									required
								/>
							</div>
						</div>

						{/* Email field */}
						<div className="space-y-2">
							<Label htmlFor="email" className="text-beige/90">Email</Label>
							<Input
								id="email"
								type="email"
								placeholder="your@email.com"
								className="bg-warmgray border-gold/20 text-beige placeholder:text-beige/40 focus:border-electric focus:ring-electric"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								required
							/>
						</div>

						{/* Password fields */}
						<div className="space-y-2">
							<Label htmlFor="password" className="text-beige/90">Password</Label>
							<Input
								id="password"
								type="password"
								placeholder="••••••••"
								className="bg-warmgray border-gold/20 text-beige placeholder:text-beige/40 focus:border-electric focus:ring-electric"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								autoComplete="new-password"
							/>
						</div>

						<div className="space-y-2">
							<Label htmlFor="password_confirmation" className="text-beige/90">Confirm Password</Label>
							<Input
								id="password_confirmation"
								type="password"
								placeholder="••••••••"
								className="bg-warmgray border-gold/20 text-beige placeholder:text-beige/40 focus:border-electric focus:ring-electric"
								value={passwordConfirmation}
								onChange={(e) => setPasswordConfirmation(e.target.value)}
								autoComplete="new-password"
							/>
						</div>

						{/* Profile image (optional) */}
						<div className="space-y-2">
							<Label htmlFor="image" className="text-beige/90">Profile Image (optional)</Label>
							<div className="flex items-center gap-4">
								{imagePreview && (
									<div className="relative w-16 h-16 rounded-lg overflow-hidden ring-2 ring-gold/40">
										<Image
											src={imagePreview}
											alt="Profile preview"
											fill
											className="object-cover"
										/>
									</div>
								)}
								<div className="flex-1 flex items-center gap-2">
									<Input
										id="image"
										type="file"
										accept="image/*"
										onChange={handleImageChange}
										className="bg-warmgray border-gold/20 text-beige file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-gold file:text-carbon hover:file:bg-gold/80 transition-all"
									/>
									{imagePreview && (
										<Button
											variant="ghost"
											size="icon"
											className="text-beige/60 hover:text-destructive hover:bg-destructive/10"
											onClick={() => {
												setImage(null);
												setImagePreview(null);
											}}
										>
											<X className="h-4 w-4" />
										</Button>
									)}
								</div>
							</div>
						</div>

						{/* Sign up button */}
						<Button
							className="w-full bg-gradient-gold hover:opacity-90 text-carbon font-bold shadow-premium transition-all duration-300 hover:scale-[1.02]"
							disabled={loading}
							onClick={async () => {
								try {
									await signUp.email({
										email,
										password,
										name: `${firstName} ${lastName}`,
										image: image ? await convertImageToBase64(image) : "",
										callbackURL: "/dashboard",
										fetchOptions: {
											onResponse: () => setLoading(false),
											onRequest: () => setLoading(true),
											onError: (ctx) => {
												console.error("Signup error:", ctx.error);
												toast.error(ctx.error.message || "Failed to create account");
											},
											onSuccess: async () => {
												toast.success("Account created successfully! Logging you in...");
												// Auto-login après signup
												try {
													await signIn.email({
														email,
														password,
													}, {
														onSuccess: () => {
															router.push("/dashboard");
														},
														onError: (ctx) => {
															toast.info("Please sign in to continue");
															router.push("/signin");
														}
													});
												} catch (error) {
													toast.info("Please sign in to continue");
													router.push("/signin");
												}
											},
										},
									});
								} catch (error: any) {
									console.error("Signup exception:", error);
									toast.error(error.message || "An unexpected error occurred");
									setLoading(false);
								}
							}}
						>
							{loading ? (
								<>
									<Loader2 className="mr-2 h-4 w-4 animate-spin" />
									Creating account...
								</>
							) : (
								<>
									<Sparkles className="mr-2 h-4 w-4" />
									Create Account
								</>
							)}
						</Button>
					</CardContent>

					<CardFooter className="flex flex-col gap-2 pt-2">
						<div className="text-center text-sm text-beige/60">
							Already have an account?{" "}
							<Link href="/signin" className="text-gold hover:text-gold/80 font-semibold transition-colors">
								Sign in
							</Link>
						</div>
					</CardFooter>
				</Card>

				{/* Footer */}
				<p className="text-center text-xs text-beige/40 mt-8">
					© 2025 CrossIt. Premium cross-listing platform.
				</p>
			</div>
		</div>
	);
}

async function convertImageToBase64(file: File): Promise<string> {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.onloadend = () => resolve(reader.result as string);
		reader.onerror = reject;
		reader.readAsDataURL(file);
	});
}
