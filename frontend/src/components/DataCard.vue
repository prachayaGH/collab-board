<script setup lang="ts">
const props = defineProps<{
  icon: string;
  color?: string;
  label: string;
  value: number;
}>();
</script>

<template>
    <div
      class="flex items-center shadow-xl py-7 px-5 border-1 border-gray-200 rounded-[8px] justify-between"
    >
      <div class="ml-4">
        <div class="text-sm text-gray-500">{{ props.label }}</div>
        <div class="text-4xl font-bold text-gray-900">{{ props.value }}</div>
      </div>
      <div class="flex-shrink-0">
        <div
          class="w-12 h-12 rounded-lg flex items-center justify-center"
          :style="{ backgroundColor: props.color }"
        >
          <i :class="icon"></i>
        </div>
      </div>
    </div>
</template>

<style scoped>
.fa-people-group {
  color: #16A34A;
  font-size: 18px;
}

.fa-door-open {
  color: #2563EB;
  font-size: 18px;
}

.fa-file {
  color: #EA580C;
  font-size: 18px;
}

.fa-message{
  color: #9333EA;
  font-size: 18px;
}

</style>
