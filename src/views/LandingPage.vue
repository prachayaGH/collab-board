<script setup lang="ts">
import Navbar from "@/components/common/Navbar.vue";
import FeatureCards from "@/components/common/FeatureCards.vue";
import Footer from "@/components/common/Footer.vue";
// import { useRouter } from 'vue-router';

const featureData = [
  {
    icon: "fa-solid fa-comments",
    bgColor: "#EFEFFE",
    title: "Real-time Chat",
    description:
      "Instant messaging with your team members. See who's typing and get messages as they happen.",
  },
  {
    icon: "fa-solid fa-bell",
    bgColor: "#F3EEFE",
    title: "Smart Notifications",
    description:
      "Get notified about important updates, mentions, and activities without missing anything.",
  },
  {
    icon: "fa-solid fa-share-nodes",
    bgColor: "#E6F8FB",
    title: "File Sharing",
    description:
      "Share files and create short links for easy collaboration. Coming soon to enhance your workflow.",
  },
  {
    icon: "fa-solid fa-shield-halved",
    bgColor: "#E8F9EF",
    title: "Secure Login",
    description:
      "Sign in securely with Google or GitHub OAuth 2.0. Your data is protected and encrypted.",
  },
  {
    icon: "fa-solid fa-bolt",
    bgColor: "#FDECEC",
    title: "Lightning Fast",
    description:
      "Experience real-time updates with minimal latency. Built for speed and reliability.",
  },
  {
    icon: "fa-solid fa-people-group",
    bgColor: "#F6EEFE",
    title: "Team Collaboration",
    description:
      "Work together seamlessly with your team. See who's online and collaborate in real-time.",
  },
];

const dashboardData = [
  {
    number: "10K",
    title: "Active Teams"
  },
  {
    number: "99.9%",
    title: "Uptime"
  },
  {
    number: "50M",
    title: "Messages Sent"
  },
  {
    number: "150+",
    title: "Countries"
  }
]

// const router = useRouter();

// function goToLogin() {
//   router.push('/login');
// }
</script>

<template>
  <div>
    <header class="md:px-25 px-10 border-2 border-gray-200 bg-white sticky top-0 z-50">
      <Navbar />
    </header>

    <main class="md:px-25 px-10 mt-25 mb-30 flex flex-col justify-center items-center text-center ">
      <h1 class="md:text-[60px] text-[40px] font-bold md:w-[700px]">Real-time Collaboration <span class="text-[#6366F1]">Made Simple</span></h1>
      <p class="mt-5 mb-10 md:w-[750px] heading-2">
        Empower your team with lightning-fast collaboration tools. Share ideas, work together seamlessly, and achieve
        more with our secure platform.
      </p>
      <div class="flex flex-row md:gap-15 gap-8">
        <button class="btn--primary px-8 py-4 rounded-xl text-[18px] font-semibold shadow-2xl shadow-[#6366F1] cursor-pointer">
          🚀 Get Started Free
        </button>
        <button class="text-[18px] font-semibold text-gray-600 cursor-pointer">
          ▶️ Watch Demo
        </button>
      </div>
    </main>

    <div class="features-section bg-gray-50 md:px-25 px-10 flex flex-col justify-center items-center pt-15 mb-20">
      <h1 class="text-4xl font-bold">Powerful Features</h1>
      <p class="mt-4 my-10 heading-2 text-center">Everything you need for seamless collaboration</p>
      <div class="md:grid md:grid-cols-3 grid grid-cols-1 gap-10 mb-20 mt-5">
        <FeatureCards v-for="feature of featureData" :key="feature.title" :icon="feature.icon" :color="feature.bgColor"
          :title="feature.title" :description="feature.description" />
      </div>
    </div>

    <div class="md:grid md:grid-cols-4 grid grid-cols-1 md:px-25 gap-10 px-10 mb-20">
      <div v-for="data of dashboardData" :key="data.title" class="text-center">
        <h1 class="text-4xl font-bold text-[#6366F1]">{{data.number}}</h1>
        <p class="text-gray-600 mt-2">{{data.title}}</p>
      </div>
    </div>

    <div class="bg-[#6366F1] w-full text-center text-white md:px-25 px-10 py-18">
      <h1 class="text-4xl font-bold">Ready to Start Collaborating?</h1>
      <p class="my-5 text-[18px]">Join thousands of teams already using CollabChat for their daily collaboration needs.</p>
      <button class="mt-2 py-3 px-8 rounded-[8px] bg-white cursor-pointer text-[#6366F1] font-bold">Sing Up</button>
      <!-- Animation -->
    </div>
    <Footer />
  </div>
</template>
