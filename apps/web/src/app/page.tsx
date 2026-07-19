import { BrandBrain } from "@/components/brand-brain/BrandBrain";
import { ContentStudio } from "@/components/content-studio/ContentStudio";
import { DashboardHero } from "@/components/dashboard/DashboardHero";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { AppShell } from "@/components/layout/AppShell";
import { ResearchHub } from "@/components/research-hub/ResearchHub";

export default function HomePage() {
  return (
    <AppShell>
      <div className="space-y-8" id="top">
        <DashboardHero />
        <DashboardStats />
        <QuickActions />
        <BrandBrain />
        <ResearchHub />
        <ContentStudio />
      </div>
    </AppShell>
  );
}
