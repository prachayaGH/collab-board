<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useSocket } from "@/composables/useSocket";

</script>

<template>
  <main class="">
    <router-view />
  </main>
</template>

<style scoped>
</style>




