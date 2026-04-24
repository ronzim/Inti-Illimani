<template>
  <div
    class="bg-slate-800/80 backdrop-blur-md p-4 rounded-xl border border-slate-700 shadow-lg flex-1"
  >
    <div class="flex items-center justify-between mb-2">
      <span class="text-slate-400 text-sm font-medium">{{ title }}</span>
      <component
        :is="iconComponent[icon]"
        class="w-5 h-5"
        :class="colorClass"
      />
    </div>
    <div class="flex items-baseline">
      <span class="text-2xl font-bold text-white">{{ value }}</span>
      <span v-if="unit" class="ml-1 text-slate-400 text-sm">{{ unit }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import {
  AlertTriangle,
  Activity,
  ArrowDownToLine,
  Info,
  MapPin,
  Map,
  Box
} from "lucide-vue-next";

defineProps({
  title: String,
  value: [String, Number],
  unit: String,
  icon: String,
  colorClass: String
});

const iconComponent = {
  "alert-triangle": AlertTriangle,
  activity: Activity,
  "arrow-down-to-line": ArrowDownToLine,
  info: Info,
  "map-pin": MapPin,
  map: Map,
  box: Box
};
</script>
