<script setup lang="ts">

const props = defineProps<{
  icon: string
  color?: string
  title: string
  description: string
}>()

</script>

<template>
  <div class="feature-card p-5 rounded-[12px] border-1 border-gray-200 shadow-xl">
    <div class="icon w-15 h-15 content-center text-center rounded-[8px] mb-6"
    :style="{ backgroundColor: props.color || 'white' }">
      <i :class="icon"></i>
    </div>
    <h3 class="font-semibold my-3 text-[20px]">{{ props.title }}</h3>
    <p class="text-gray-600 pr-15">{{  props.description }}</p>
  </div>
</template>

<style scoped>
.fa-comments {
  color: #6366F1;
  font-size: 24px;
}

.fa-bell {
  color: #8B5CF6;
  font-size: 24px;
}

.fa-share-nodes {
  color: #08B7D4;
  font-size: 24px;
}

.fa-shield-halved {
  color: #22C55E;
  font-size: 24px;
}

.fa-bolt {
  color: #EF4444;
  font-size: 24px;
}

.fa-people-group {
  color: #A855F7;
  font-size: 24px;
}
</style>
