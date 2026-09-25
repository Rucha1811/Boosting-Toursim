import type { Destination } from "./types";

export interface DestCopy {
  short: string;
  searchHint: string;
  makersLine: string;
  festivalLine: string;
  guideQuote: string;
  guideAnswer: string;
  itineraryTrail: string;
  itineraryStops: [string, string][];
  assistantIntro: string;
  assistantSuggestions: string[];
}

const VAD = "Vadodara";
const AHD = "Ahmedabad";
const KUT = "Kutch";
const JPR = "Jaipur";
const VRS = "Varanasi";

export const destCopy: Record<number, DestCopy> = {
  1: {
    short: VAD,
    searchHint: "Search Laxmi Vilas, Kansara Bazaar, garba…",
    makersLine: "From beaded wooden stallions to Pithora walls painted by Rathwa hands — discover the artisans and local makers who open their workshops to visitors, and buy direct.",
    festivalLine: "Navratri, Uttarayan, Holi — plan around them.",
    guideQuote: "“We have one evening — what should we do?”",
    guideAnswer: "Start at Laxmi Vilas Palace, catch the EME temple at dusk, then join the garba at Darbargadh. The map will keep you one step ahead of the crowds.",
    itineraryTrail: "Follow the amber heritage trail from Laxmi Vilas Palace through Kansara Bazaar to Mandvi Gate, then pause at Nyay Mandir before the evening garba during Navratri.",
    itineraryStops: [
      ["Morning", "Laxmi Vilas Palace → EME Temple"],
      ["Lunch", "Sasumaa ni ... food in Raopura — try sev-usal"],
      ["Afternoon", "Baroda Museum & Picture Gallery"],
      ["Evening", "Mandvi Gate sunset → Navratri garba at Truth & Darbargadh"],
    ],
    assistantIntro: "Namaste! I'm the Virsa Guide — I know the heritage, the festivals, the makers, the food and the live crowd situation around Vadodara right now. Ask me anything, or pick a suggestion below.",
    assistantSuggestions: [
      "We have one evening in Vadodara — what should we do?",
      "Where can we see Navratri garba this week?",
      "Best place to buy authentic beadwork gifts?",
      "Which places are least crowded right now?",
      "Vegetarian food near Laxmi Vilas Palace?",
      "Are there any road closures today?",
    ],
  },
  2: {
    short: AHD,
    searchHint: "Search Sabarmati Ashram, pol houses, Manek Chowk…",
    makersLine: "From hand-block printed textiles to the filigree stonemasons of the old city — meet the Ahmedabad artisans who open their workshops to visitors, and buy direct.",
    festivalLine: "Navratri, Uttarayan, International Kite Festival — plan around them.",
    guideQuote: "“I have one day downtown — what's unmissable?”",
    guideAnswer: "Walk the pol lanes of Khadia at dawn, see the Sidi Saiyyed 'Tree of Life' jali at dusk, and finish with the night street-food of Manek Chowk.",
    itineraryTrail: "Follow the heritage lane from Gandhi's Sabarmati Ashram through the pol-houses of the walled city to the evening lights of the Sabarmati riverfront.",
    itineraryStops: [
      ["Morning", "Sabarmati Ashram → Hathi Singh Jain temple"],
      ["Lunch", "Home-food in a Khadia pol, then old-city khaudra"],
      ["Afternoon", "Adalaj stepwell → Calico Museum (slot)"],
      ["Evening", "Sidi Saiyyed jali at dusk → riverfront promenade"],
    ],
    assistantIntro: "Namaste! I'm the Virsa Guide — I know the heritage, the pols, the festivals, the makers, the food and the live crowd situation around Ahmedabad right now. Ask me anything, or pick a suggestion below.",
    assistantSuggestions: [
      "One evening in Ahmedabad — what should we do?",
      "Where can we see Navratri garba this week?",
      "Best place to buy authentic hand-block-printed fabric?",
      "Which places are least crowded right now?",
      "Vegetarian food near the old-city pols?",
      "Are there any road closures today?",
    ],
  },
  3: {
    short: KUT,
    searchHint: "Search white desert, Bhujodi weavers, Rogan art…",
    makersLine: "From bell-metal camels to Rogan painting and Ajrakh block-prints — meet the master-craftspeople of Kutch who open their village workshops, and buy direct.",
    festivalLine: "Rann Utsav, Bhuj heritage festival, Kutch boat festival — plan around them.",
    guideQuote: "“Two days around the Rann — what do we plan?”",
    guideAnswer: "Start with the Aina Mahal and Prag Mahal in Bhuj, weave through Bhujodi village, then end at the moonlit white desert of the great Rann.",
    itineraryTrail: "Follow the craft trail from Bhuj's palaces to Bhujodi's weavers, Nirona's bronze bells and the salt-flat horizon of the great Rann.",
    itineraryStops: [
      ["Morning", "Aina Mahal & Prag Mahal, Bhuj"],
      ["Lunch", "Bhujodi — local thali by the weavers' square"],
      ["Afternoon", "Nirona: bell-metal & Rogan art demos"],
      ["Evening", "White Rann / Dhordo sunset on the salt"],
    ],
    assistantIntro: "Namaste! I'm the Virsa Guide — I know the craft villages, the Rann, the festivals, the makers, the food and the live crowd situation around Kutch right now. Ask me anything, or pick a suggestion below.",
    assistantSuggestions: [
      "Two days in Kutch — what should we plan?",
      "When is the next Rann Utsav and how do we get there?",
      "Where can we see live Rogan and bell-metal work?",
      "Which places are least crowded right now?",
      "Best place to buy authentic Ajrakh textiles?",
      "Are there any road closures today?",
    ],
  },
  4: {
    short: JPR,
    searchHint: "Search Amber Fort, Hawa Mahal, Johari Bazaar…",
    makersLine: "From blue pottery and block-printing to gota and zardozi — meet the Pink City's makers who open their workshops, and buy direct.",
    festivalLine: "Teej, Gangaur, Kite Festival, Literature Festival — plan around them.",
    guideQuote: "“One full day in Jaipur — best route?”",
    guideAnswer: "Start at Amber Fort at sunrise, ride down through the walled city to Hawa Mahal, shop Johari Bazaar and the bazaar lanes, then finish with lassi in the old city.",
    itineraryTrail: "Ride the Pink City from Amber Fort's ramparts through the walled bazaars to the observatory and Hawa Mahal's jharokha wall.",
    itineraryStops: [
      ["Morning", "Amber Fort sunrise → Nahargarh view"],
      ["Lunch", "Masala Chowk street food near Albert Hall"],
      ["Afternoon", "Johari Bazaar: blue pottery, gota, zardozi"],
      ["Evening", "Hawa Mahal facade → Jantar Mantar at dusk"],
    ],
    assistantIntro: "Namaste! I'm the Virsa Guide — I know the forts, the bazaars, the festivals, the makers, the food and the live crowd situation around Jaipur right now. Ask me anything, or pick a suggestion below.",
    assistantSuggestions: [
      "One full day in Jaipur — best route?",
      "Where can we catch the next Teej celebration?",
      "Best place to buy authentic blue pottery and gota?",
      "Which places are least crowded right now?",
      "Vegetarian food in the walled city?",
      "Are there any road closures today?",
    ],
  },
  5: {
    short: VRS,
    searchHint: "Search ghats, Kashi Vishwanath, silk looms…",
    makersLine: "From Banarasi silk on pit-looms to Gulabi meenakari and hand-carved wooden toys — meet Varanasi's makers on the lanes behind the ghats, and buy direct.",
    festivalLine: "Dev Deepawali, Ganga Mahotsav, Shivratri — plan around them.",
    guideQuote: "“We're here two nights on the ghats — what do we do?”",
    guideAnswer: "Take the dawn boat from Assi to the old city, walk the Kashi Vishwanath lane, visit a silk loom at Madhopatti, and end at the Dashashwamedh aarti.",
    itineraryTrail: "Live the ghats from Assi's sunrise to Dashashwamedh's aarti, threading the old-city lanes past the silk looms and temple bazaars.",
    itineraryStops: [
      ["Morning", "Sunrise boat: Assi → Dashashwamedh"],
      ["Lunch", "Kachori-jalebi on the Godowlia food lane"],
      ["Afternoon", "Silk looms at Madhopatti → Gulabi enamel studio"],
      ["Evening", "Dashashwamedh aarti → evening boat on the Ganga"],
    ],
    assistantIntro: "Namaste! I'm the Virsa Guide — I know the ghats, the temples, the festivals, the silk, the food and the live crowd situation around Varanasi right now. Ask me anything, or pick a suggestion below.",
    assistantSuggestions: [
      "We have two nights on the ghats — what should we do?",
      "Where can we catch the evening aarti best?",
      "Best place to buy Banarasi silk directly?",
      "Which places are least crowded right now?",
      "Where does the sunrise boat sail from?",
      "Are there any road closures today?",
    ],
  },
};

const FALLBACK: DestCopy = {
  short: "this heritage city",
  searchHint: "Search a landmark, bazaar or festival…",
  makersLine: "From handcrafted treasures to living workshops — discover the artisans and local makers who open their doors to visitors, and buy direct.",
  festivalLine: "Check the festival calendar and plan around the big moments.",
  guideQuote: "“We have one day — what should we do?”",
  guideAnswer: "Follow the heritage trail in the morning, meet a local maker after lunch, and catch the evening festival or aarti before the night food lane.",
  itineraryTrail: "Follow the community's heritage trail from the landmark quarter through the artisan bazaar to the evening festival lights.",
  itineraryStops: [
    ["Morning", "Heritage landmark walk"],
    ["Lunch", "Local food lane favourites"],
    ["Afternoon", "Artisan workshop visit"],
    ["Evening", "Festival lights / live music"],
  ],
  assistantIntro: "Namaste! I'm the Virsa Guide — I know the heritage, the festivals, the makers, the food and the live crowd situation here right now. Ask me anything, or pick a suggestion below.",
  assistantSuggestions: [
    "We have one day here — what should we do?",
    "What's happening in the city this week?",
    "Best place to buy authentic local crafts?",
    "Which places are least crowded right now?",
    "Vegetarian food recommendations?",
    "Are there any road closures today?",
  ],
};

export function destShort(d: Destination | null | undefined): string {
  if (!d) return "this heritage city";
  return d.name.replace(/\s+Tourism$/, "");
}

export function getDestCopy(id: number): DestCopy {
  return destCopy[id] ?? FALLBACK;
}