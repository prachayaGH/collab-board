<script setup lang="ts">
import Navbar from "@/components/common/Navbar.vue";
import DataCard from "@/components/DataCard.vue";

const stats = [
  {
    label: "ผู้ใช้ออนไลน์",
    value: "24",
    color: "#DCFCE7",
    icon: "fa-solid fa-people-group",
  },
  {
    label: "ห้องที่เปิดใช้งาน",
    value: "8",
    color: "#DBEAFE",
    icon: "fa-solid fa-door-open",
  },
  {
    label: "ข้อความทั้งหมด",
    value: "156",
    color: "#F3E8FF",
    icon: "fa-solid fa-message",
  },
  {
    label: "ไฟล์แชร์",
    value: "32",
    color: "#FFEDD5",
    icon: "fa-solid fa-file",
  },
];
</script>

<template>
  <div class="md:px-25 px-10 border-2 border-gray-200 bg-white sticky top-0 z-50">
    <Navbar />
  </div>

  <main class="max-w-7xl mt-5 mx-12 md:mx-auto">
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      <DataCard v-for="stat of stats" :key="stat.label" :icon="stat.icon" :color="stat.color"
          :label="stat.label" :value="Number(stat.value)" />
    </div>
  </main>
</template>
