<template>
  <div class="chat-window flex flex-col h-full border-l-1 border-r-1 border-gray-200">
    <!-- Chat Header -->
    <div
      class="chat-header flex items-center justify-between p-4 border-b border-gray-200 bg-white"
    >
      <div class="flex items-center space-x-3">
        <button @click="$emit('close')" class="md:hidden p-2 hover:bg-gray-100 rounded-full">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            ></path>
          </svg>
        </button>
        <div class="relative">
          <img
            src="https://cms.dmpcdn.com/news/2024/02/18/7b9a93d0-ce44-11ee-beed-ff7a7b5994ed_original.jpg"
            alt=""
            class="w-8 h-8 rounded-full"
          />
          <div
            class="absolute -bottom-1 -right-0 w-3 h-3 rounded-full border-2 border-white bg-green-500"
          ></div>
        </div>
        <div>
          <div class="font-medium">friend [chat]</div>
          <div class="text-sm text-gray-500">online</div>
        </div>
      </div>
      <div class="flex items-center space-x-4">
        <i class="fas fa-phone text-gray-600 cursor-pointer hover:text-gray-500"></i>
        <i class="fas fa-video text-gray-600 cursor-pointer hover:text-gray-500"></i>
        <i class="fas fa-exclamation-circle text-gray-600 cursor-pointer hover:text-gray-500"></i>
      </div>
    </div>

    <!-- Messages Container -->
    <div ref="messagesContainer"
      class="messages-container flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
      <div class="message flex items-start space-x-3">
        <img
          class="w-8 h-8 rounded-full inline-block mr-2"
          src="https://cms.dmpcdn.com/news/2024/02/18/7b9a93d0-ce44-11ee-beed-ff7a7b5994ed_original.jpg" alt="">
        <div class="flex flex-col gap-2">
          <h4 class="text-[16px]">friend [chat] <span class="text-[10px] text-gray-500">10:30 AM</span></h4>
          <p class="text-[14px] text-gray-700">Hey friend! Lorem ipsum dolor sit amet consectetur adipisicing elit. Impedit perferendis nemo debitis quod reprehenderit ullam veritatis, dolorem culpa incidunt omnis nihil sapiente nesciunt laboriosam ipsa neque odio. Voluptate, aliquid dignissimos!</p>
          <div class="flex space-x-2 text-gray-500 text-xs mt-1">
            <i class="fa-regular fa-thumbs-up text-[10px]"> 2</i>
            <i class="fa-solid fa-share"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Input -->
    <div class="message-input p-4 border-t border-gray-200 bg-white">
      <div class="flex space-x-4">
        <i class="fa-solid fa-paperclip items-center content-center p-1"></i>
        <input
          type="text"
          placeholder="Type a message..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-[8px] focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        <button
          class="p-2 w-10 bg-blue-500 text-white rounded-[8px] hover:bg-blue-600 cursor-pointer"
        >
          <i class="fa-solid fa-paper-plane"></i>
        </button>
      </div>
    </div>
  </div>
</template>
