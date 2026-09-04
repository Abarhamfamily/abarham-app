import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { BottomNav, type Route as NavRoute } from "@/components/app/bottom-nav";
import {
  TopBar,
  HeroCard,
  CategoryRail,
  UpcomingTrip,
  FeaturedRail,
  Community,
} from "@/components/app/sections";
import { Icon } from "@/components/app/icon";
import { TripsScreen } from "@/components/app/trips";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "آبرهام — سفرهای طبیعت‌گردی" },
      {
        name: "description",
        content:
          "آبرهام، جامعه طبیعت‌گردان ایرانی. سفرهای بکر کوهستان، جنگل، دره‌نوردی و کمپ با راهنمایان مجرب.",
      },
      { property: "og:title", content: "آبرهام — سفرهای طبیعت‌گردی" },
      {
        property: "og:description",
        content:
          "طبیعت بکر ایران در انتظار توست. با راهنمایان مجرب آبرهام همراه شو و به جامعه طبیعت‌گردان بپیوند.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "/" }],
  }),
});

const placeholderTabs: Partial<Record<NavRoute, { icon: string; text: string }>> = {
  wallet: { icon: "account_balance_wallet", text: "کیف سفر شما خالی است" },
  notifications: { icon: "notifications", text: "اعلان جدیدی ندارید" },
  profile: { icon: "person", text: "پروفایل شما" },
};

function Index() {
  const [active, setActive] = useState<NavRoute>("home");

  return (
    <div className="mx-auto flex min-h-[100dvh] w-full max-w-md flex-col bg-background">
      <main className="flex-1 pb-6">
        {active === "home" ? (
          <>
            <TopBar />
            <HeroCard />
            <CategoryRail />
            <UpcomingTrip />
            <FeaturedRail />
            <Community />
          </>
        ) : active === "trips" ? (
          <TripsScreen />
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 px-6 pt-32 text-center">
            <span className="grid h-16 w-16 place-items-center rounded-3xl bg-secondary text-secondary-foreground">
              <Icon
                name={placeholderTabs[active]?.icon ?? "hourglass_empty"}
                size={32}
              />
            </span>
            <p className="text-sm font-medium text-muted-foreground">
              {placeholderTabs[active]?.text ?? "بزودی"}
            </p>
          </div>
        )}
      </main>
      <BottomNav active={active} onChange={setActive} />
    </div>
  );
}
