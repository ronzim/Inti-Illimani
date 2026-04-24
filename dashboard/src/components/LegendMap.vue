<template>
  <div
    class="absolute bottom-8 right-8 bg-slate-800/90 backdrop-blur-md p-4 rounded-xl border border-slate-700 shadow-xl w-64 z-10 pointer-events-none"
  >
    <h3 class="text-sm font-bold text-slate-200 mb-3 uppercase tracking-wider">
      Livello di Rischio (POF)
    </h3>

    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div
            class="w-4 h-4 rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)]"
          ></div>
          <span class="text-sm text-slate-300">Critico</span>
        </div>
        <span class="text-xs text-slate-400">&gt; 0.8</span>
      </div>

      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div
            class="w-4 h-4 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.6)]"
          ></div>
          <span class="text-sm text-slate-300">Alto</span>
        </div>
        <span class="text-xs text-slate-400">0.5 - 0.8</span>
      </div>

      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div
            class="w-4 h-4 rounded-full bg-yellow-400 shadow-[0_0_8px_rgba(250,204,21,0.6)]"
          ></div>
          <span class="text-sm text-slate-300">Moderato</span>
        </div>
        <span class="text-xs text-slate-400">0.2 - 0.5</span>
      </div>

      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div
            class="w-4 h-4 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.4)]"
          ></div>
          <span class="text-sm text-slate-300">Basso</span>
        </div>
        <span class="text-xs text-slate-400">&lt; 0.2</span>
      </div>
    </div>

    <div class="mt-4 pt-3 border-t border-slate-700">
      <p class="text-xs text-slate-400 italic">
        L'altezza delle colonne indica la profondità dell'anomalia (mm).
      </p>
    </div>
  </div>
</template>
