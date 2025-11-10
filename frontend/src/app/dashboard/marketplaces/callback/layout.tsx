// Layout for OAuth callbacks - NO authentication required
// This allows OAuth providers to redirect here without being blocked by Better Auth

export default function CallbackLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

