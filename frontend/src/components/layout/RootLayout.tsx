interface Props {
  children: React.ReactNode;
}

export function RootLayout({ children }: Props) {
  return (
    <div className="min-h-screen bg-[#FFF7EC] font-body text-[#23131E]">
      <a
        href="#main-content"
        className="skip-link sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:rounded-lg focus:bg-[#FC9A64] focus:text-[#23131E] focus:font-medium focus:shadow-md"
      >
        Skip to content
      </a>
      <main id="main-content">{children}</main>
    </div>
  );
}
