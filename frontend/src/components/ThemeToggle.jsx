import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

export default function ThemeToggle() {
  // Initialize state from localStorage to prevent flicker
  const [dark, setDark] = useState(() => {
    // console.log("1. Initializing theme...");
    const saved = localStorage.getItem("theme");
    if (saved) {
      // console.log(`   Found saved theme in localStorage: '${saved}'`);
      return saved === "dark";
    }
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    // console.log(`   No saved theme. Browser prefers dark: ${prefersDark}`);
    return prefersDark;
  });

  // This effect runs whenever the 'dark' state changes
  useEffect(() => {
    // document.getElementById("root").classList.toggle("dark");
    // document.getElementById("homeroot").classList.toggle("dark");
    // console.log(`3. Effect running because 'dark' is now: ${dark}`);
    if (dark) {
      // console.log("   Adding 'dark' class to <html> and saving to localStorage.");
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      // console.log("   Removing 'dark' class from <html> and saving to localStorage.");
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
    // console.log(`   Current <html> classes: '${document.documentElement.className}'`);
  }, [dark]);

  const toggleTheme = () => {
    // console.log("2. Toggle button clicked!");
    // This will trigger the useEffect hook because the state changes
    setDark(prevDark => !prevDark); 
  };

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-full bg-slate-200 dark:bg-slate-800 hover:scale-105 transition-all duration-300"
      aria-label="Toggle theme"
    >
      {dark ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-indigo-600" />}
    </button>
  );
}