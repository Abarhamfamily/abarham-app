import heroForest from "@/assets/hero-forest.jpg";
import tripMasouleh from "@/assets/trip-masouleh.jpg";
import tripHyrkanian from "@/assets/trip-hyrkanian.jpg";
import tripChakroud from "@/assets/trip-chakroud.jpg";
import tripZagros from "@/assets/trip-zagros.jpg";

export type Trip = {
  id: string;
  title: string;
  image: string;
  price: string;
  duration: string;
  difficulty: "آسان" | "متوسط" | "سخت";
  activity: string;
  capacity?: string;
  full?: boolean;
};

export const heroImage = heroForest;

export const upcomingTrip = {
  title: "پیمایش جنگل‌های ماسوله",
  startsIn: "شروع در ۲ روز",
  dates: "۲۴ آبان - ۲۶ آبان",
  companions: "۱۵ همسفر",
  description:
    "پیمایش در مسیرهای بکر و ناشناخته گیلان به همراه شب‌مانی در کلبه‌های چوبی.",
  image: tripMasouleh,
};

export const featuredTrips: Trip[] = [
  {
    id: "hyrkanian",
    title: "اکسپدیشن هیرکانی",
    image: tripHyrkanian,
    price: "۲.۵ میلیون",
    duration: "۳ روز",
    difficulty: "آسان",
    activity: "جنگل‌نوردی",
    capacity: "۸ نفر ظرفیت باقی‌مانده",
  },
  {
    id: "chakroud",
    title: "فرود از دره چاکرود",
    image: tripChakroud,
    price: "۳.۲ میلیون",
    duration: "۲ روز",
    difficulty: "سخت",
    activity: "دره‌نوردی فنی",
    full: true,
  },
  {
    id: "zagros",
    title: "شب‌مانی خط‌الراس زاگرس",
    image: tripZagros,
    price: "۱.۸ میلیون",
    duration: "۴ روز",
    difficulty: "متوسط",
    activity: "کوهپیمایی",
    capacity: "۳ نفر ظرفیت باقی‌مانده",
  },
];

export const categories = [
  { icon: "landscape", label: "کوهستان", tint: "oklch(0.62 0.1 230)" },
  { icon: "forest", label: "جنگل", tint: "oklch(0.55 0.12 150)" },
  { icon: "camping", label: "کمپ", tint: "oklch(0.66 0.13 70)" },
  { icon: "waterfall_chart", label: "دره‌نوردی", tint: "oklch(0.6 0.13 200)" },
  { icon: "kayaking", label: "رفتینگ", tint: "oklch(0.6 0.16 280)" },
];
