import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "../components/sidebar";
import { Header } from "../components/header";

export const metadata: Metadata = {
  title: "TraceX - OSINT Intelligence Platform",
  description: "Open-Source Intelligence gathering and investigation platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background font-sans antialiased">
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <div className="flex flex-col flex-1 overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto p-6">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}