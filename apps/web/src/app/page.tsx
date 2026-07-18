import { ContentStudio } from "@/components/content-studio/ContentStudio";
import { DashboardHero } from "@/components/dashboard/DashboardHero";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { AppShell } from "@/components/layout/AppShell";

export default function HomePage() {
  return (
    <AppShell>
      <div className="space-y-8">
        <DashboardHero />
        <DashboardStats />
        <QuickActions />
        <ContentStudio />
      </div>
    </AppShell>
  );
}
