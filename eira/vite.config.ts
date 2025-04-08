import { defineConfig } from 'vite'
import svgr from "vite-plugin-svgr";
import react from '@vitejs/plugin-react'
import { globSync } from "glob";
import { fileURLToPath } from 'node:url';


function getEntries(): Record<string, string> {
  const entries: Record<string, string> = {}
  
  globSync("./html/*.html").map((e) => {
    const match = e.match(/\\(.*).html/);
    // @ts-ignore
    const name: string = match[1];

    entries[name] = fileURLToPath(new URL(e, import.meta.url))
  });

  return entries
}


export default defineConfig({
  plugins: [svgr(), react()],
  build: {
    rollupOptions: {
      input: getEntries()
    }
  }
})
