<template>
  <div class="webpages-view center-content gap-16 container-xxl margin-center">
    <BasicCard
      icon="bx-list-ul"
      class="container-lg f-3"
      title="Webpages" 
      description="Manage pages from which you scrape content"
    >
      <div class="entry-list-wrapper" v-if="webpages.length > 0">
        <ListEntry
          v-for="page in webpages"
          :key="page.webpage_id"
          :item="page"
          :to="`/webpages/${page.webpage_id}`"
          icon="bx bx-globe"
          labelField="page_name"
          subField="url"
          :onEdit="editWebpage"
          :onDelete="deleteWebpage"
        />
      </div>
      <ListingPlaceholder 
        v-else
        icon="bx-globe"
        text="No webpages found"
        desc="Create a new webpage using the form on the right."
      />
    </BasicCard>
    
    <BasicCard
      icon="bx-list-plus"
      class="container-lg f-1"
      title="Create a webpage" 
      description="Set up a new page for data extraction"
    >
      <form @submit.prevent="createWebpage" class="container">
        <TextInput
          v-model="createWebpageParams.url"
          label="URL"
          placeholder="http://example.com"
        />
        <TextInput
          v-model="createWebpageParams.page_name"
          label="Page name"
          placeholder="The webpages name"
        />
        <button type="submit">Create</button>
      </form>
    </BasicCard>
  </div>
</template>

<script>
import BasicCard from '@/components/BasicCard.vue';
import ListEntry from '@/components/ListEntry.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import TextInput from '@/components/TextInput.vue'
import { fastApi } from '@/utils/fastApi';

export default {
  name: 'App',
  components: {
    BasicCard,
    ListingPlaceholder,
    TextInput,
    ListEntry,
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
        this.createWebpageParams = {};
      }
    },

    async deleteWebpage(webpage) {
      if (confirm("Are you certain you wish to delete this webpage? This action cannot be undone!")) {
        const response = await fastApi.webpages.delete(webpage.webpage_id);
        if (response) {
          await this.fetchWebpages();
        }
      }
    },

    editWebpage() {
      alert("TBD");
    },

    async fetchWebpages() {
      const response = await fastApi.webpages.get()
      if (response) {
        this.webpages = response;
      }
    },
  },

  async mounted() {
    await this.fetchWebpages()
  },

  watch: {
    // When the iframe content changes, re‑attach listeners
    previewHtml() {
      if (!this.iframeLoaded) this.attachIframeListener();
    }
  }
};
</script>

<style scoped>

</style>