<template>
  <div class="webpages-view center-content gap-16 container-xxl margin-center">
    <BasicCard
      class="container-lg f-3"
      title="Webpages" 
      description="Manage pages from which you scrape content"
    >
      <div class="webpage-wrapper">
        <router-link
          v-for="(webpage, index) in webpages" 
          :key="index" 
          :to="`/webpages/${webpage.webpage_id}`"
          class="webpage-option no-deco"
          @click="handleExpandWebpage(webpage)"
        >
          <i class="bx bx-globe"></i>
          <div class="flex-rw space-between vertical-align">
            <div class="flex-cl">
              <label>{{ webpage.page_name }}</label>
              <a :href="webpage.url">{{ webpage.url }}</a>
            </div>
            <div class="controls">
              <i @click.prevent class="bx bxs-edit btn btn-text btn-icon"></i>
              <i @click.prevent class="bx bxs-trash btn btn-text btn-icon btn-danger"></i>
            </div>
          </div>
        </router-link>
      </div>
    </BasicCard>
    
    <BasicCard
      class="container-lg f-1"
      title="Create a webpage" 
      description="Set up a new page for data extraction"
    >
      <form @submit.prevent="createWebpage" class="container">
        <div>
          <label for="">URL</label>
          <input type="text" v-model="createWebpageParams.url">
        </div>
        <div>
          <label for="">Page name</label>
          <input type="text" v-model="createWebpageParams.page_name">
        </div>
        <div>
          <button type="submit">Create</button>
        </div>
      </form>
    </BasicCard>
  </div>
</template>

<script>
import BasicCard from '@/components/BasicCard.vue';
import { fastApi } from '@/utils/fastApi';

export default {
  name: 'App',
  components: {
    BasicCard
  },
  data() {
    return {
      previewHtml: null,          // the HTML string for the iframe
      previewIframe: null,        // will be set via $refs
      clickedElement: "",         // selected element inside the iframe
      locator: "",
      inputUrl: "",
      createWebpageParams: {
        url: "",
        page_name: ""
      },
      targetUrl: "",
      iframeLoaded: false,          // flag to avoid re‑attaching listeners
      webpages: []
    };
  },
  methods: {
    async createWebpage() {
      const response = await fastApi.webpages.post(this.createWebpageParams);
      if (response) {
        await this.fetchWebpages();
      }
    },

    async fetchWebpages() {
      this.webpages = await fastApi.webpages.get()
    },
  },

  async mounted() {
    await this.fetchWebpages()
  },

  watch: {
    /** When the iframe content changes, re‑attach listeners */
    previewHtml() {
      if (!this.iframeLoaded) this.attachIframeListener();
    }
  }
};
</script>

<style scoped>
.webpage-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.webpage-option {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
  box-sizing: border-box;
  padding: 4px 8px;
  background-color: var(--color-neutral-200);
  border-radius: var(--btn-radius);
  cursor: pointer;
  transition: var(--t-fast) background-color;
}
.webpage-option:hover {
  background-color: var(--color-neutral-300);
}

.webpage-option label {
  cursor: pointer;
  font-weight: var(--fw-medium);
}
.webpage-option a {
  font-size: var(--fs-1);
}
.webpage-option i.bx-globe {
  font-size: var(--fs-5);
  padding-inline: 4px;
}
.webpage-option .controls {
  transition: var(--t-fast) opacity;
  opacity: 0;
}
.webpage-option:hover .controls {
  opacity: 1;
}

.webpage-option .controls i {
  font-size: var(--fs-4);
}

.webpage-option .btn:hover {
  background-color: var(--color-neutral-400);
}

</style>