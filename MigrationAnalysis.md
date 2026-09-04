# Abarham-Stitch UI Migration Analysis

## 1. Stitch UI Components

### bottom-nav.tsx
- **Purpose**: Bottom navigation bar with 5 items (home, trips, wallet, notifications, profile)
- **UI**: Sticky nav, icon buttons, active state highlighting
- **Reusable**: Yes
- **Direct copy**: Partial - structure works, routes/icons need Abarham matching
- **Needs adaptation**: Yes - match Abarham routes (no notifications), icon system
- **Replaces**: `frontend/src/components/BottomNav.tsx`

### data.ts
- **Purpose**: Static mock data for trips, categories, hero image
- **UI**: Trip data structure, featured trips array, categories, hero/upcoming objects
- **Reusable**: No - purely mock data
- **Direct copy**: No - must come from Abarham API
- **Needs adaptation**: Yes - replace with real API calls
- **Equivalent**: `/trips` API endpoint

### icon.tsx
- **Purpose**: Material Symbols Rounded icon wrapper with RTL support
- **UI**: Ligature icons, filled/outlined states, size customization
- **Reusable**: Yes
- **Direct copy**: Yes - but Abarham may have own system
- **Needs adaptation**: Only if no equivalent exists
- **Equivalent**: None - Abarham uses emoji/SVG

### sections.tsx
- **Purpose**: Home page sections (TopBar, HeroCard, CategoryRail, UpcomingTrip, FeaturedRail, Community)
- **UI**: Greeting, hero image, category chips, featured trips grid, community CTA
- **Reusable**: Yes - modular sections
- **Direct copy**: Partial - structure works, data needs API
- **Needs adaptation**: Yes - connect to real data sources
- **Replaces**: Parts of `frontend/src/pages/HomePage.tsx`

### trips.tsx
- **Purpose**: Trips screen with search, filters, favorites, trip grid
- **UI**: Search bar, filter chips, favorites scroll, trip cards with price overlay
- **Reusable**: Yes
- **Direct copy**: Partial - UI structure works, data/API need matching
- **Needs adaptation**: Yes - use Abarham trips API
- **Replaces**: `frontend/src/pages/TripsPage.tsx`

### types.ts
- **Purpose**: Exports Trip type from data.ts
- **UI**: Type definitions only
- **Reusable**: Yes
- **Direct copy**: Partial - needs Abarham Trip interface alignment
- **Needs adaptation**: Yes - align with actual Trip type
- **Equivalent**: `frontend/src/types/index.ts`

## 2. Mock/Static Data

### data.ts
- heroImage: hero-forest.jpg
- upcomingTrip: title "پیمایش جنگل‌های ماسوله", dates, companions, image
- featuredTrips: 3 trips (hyrkanian, chakroud, zagros) with images
- categories: 4 items with icons/labels

### sections.tsx
- Uses all data.ts content
- TopBar: hardcoded name "آرش"
- HeroCard: hardcoded text
- Community: hardcoded text

### trips.tsx
- trips: 2 items (shovi, badab) with images
- activeFilters: ["سختی: متوسط", "نوع: طبیعت‌گردی"]
- filterButtons: ["تاریخ", "قیمت"]

## 3. API Compatibility

| Stitch | Abarham | Compatible? | Adaptation |
|--------|---------|-------------|------------|
| id: string | id: string | Yes | None |
| title: string | title: string | Yes | None |
| image: import path | trip.images[0] | No | Use API image URL |
| price: "۲.۵ میلیون" | price: "2500000" | Partial | Format with commas + تومان |
| duration: "۳ روز" | calculate from dates | No | Compute from start/end_date |
| difficulty | difficulty_level | Yes | None |
| activity | not in API | No | New field or derive |
| capacity text | capacity/remaining_capacity | Partial | Format remaining string |
| full?: boolean | remaining_capacity <= 0 | Yes | Compute |

Missing in Stitch: destination, description, start/end_date, deposit, transportation, meeting_point, departure_time, status

## 4. HomePage Migration

1. **TopBar** - Migrate UI, adapt to auth store user data
2. **HeroCard** - Migrate UI, adapt image/text to API
3. **CategoryRail** - Migrate UI, adapt categories to API/static
4. **UpcomingTrip** - Migrate UI, needs API endpoint or use first trip
5. **FeaturedRail** - Migrate UI, use trips API with limit
6. **Community** - Migrate directly (static content)

## 5. Trips Page

Stitch adds: filter UI, favorites, price overlay on images, duration badges
Abarham has: image carousel, destination, start date, difficulty

Recommendation: Adopt Stitch's improved card UI and add filter/favorite features progressively

## 6. Bottom Navigation

| Feature | Stitch | Abarham |
|---------|--------|---------|
| Routes | 5 (has notifications) | 4 |
| Icons | Material Symbols | Emoji |
| Active style | bg-primary/12 + filled icon | bg-primary/12 |
| Labels | Persian (identical) | Persian (identical) |

Recommendation: Adopt Stitch structure, keep emoji icons (no new deps), add notifications if needed

## 7. Images/Assets

Stitch uses 7 static images (hero-forest, trip-masouleh, trip-hyrkanian, trip-chakroud, trip-zagros, trip-shovi, trip-badab).

Abarham API provides `trip.images` array - this field is missing from Trip type but used in components.

**Do NOT copy Stitch images** - use real API image URLs instead.

## 8. Dependencies

| Package | Stitch | Abarham | Needed? |
|---------|--------|---------|---------|
| @tanstack/react-router | Yes | No | Must convert to react-router-dom |
| @tanstack/react-query | Yes | Yes | Compatible |
| clsx + tailwind-merge | Yes | No | Can implement manually |
| react-router-dom | No | Yes | Keep existing |

## 9. Migration Order

1. **BottomNav** - Structural, no data deps
2. **UI Utilities** - Simple helpers, emoji icons
3. **HomePage** - Start static (Community, Categories), then API (Trips)
4. **TripDetailsPage** - UI improvements
5. **TripsPage** - Complex, leave for last
6. **Profile/Wallet/Login** - Low priority

## 10. Risk Assessment

- **High**: Routing differences (TanStack Router vs React Router DOM)
- **Medium**: Trip type mismatch (missing images field)
- **Low**: React Query compatibility (both use TanStack)
- **Low**: Mobile layout (both Tailwind responsive)

Mitigation: Careful type alignment, incremental compilation, keep API services unchanged

---

## Final Output

### READY TO MIGRATE
- icon.tsx (adapt to emoji)
- bottom-nav.tsx (structural nav)
- utils.ts (simple cn function)
- sections.tsx Community (static)
- sections.tsx CategoryRail (static categories)

### NEEDS ADAPTATION
- sections.tsx TopBar/HeroCard/UpcomingTrip/FeaturedRail (API data)
- data.ts (replace with API calls)
- trips.tsx (API integration, state management)
- types.ts (align with Abarham Trip)
- routes/index.tsx (convert TanStack Router to react-router-dom)
- routes/__root.tsx (convert providers)

### DO NOT TOUCH YET
- LoginPage/RegisterPage (form-based)
- WalletPage (simple display)
- ProfilePage (simple display)
- API service files (working)
- Store files (working)