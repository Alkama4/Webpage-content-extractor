<template>
  <div class="webpages-view">
    <h1>Webpages</h1>
    <div class="webpages-view-grid gap-16">
      <BasicCard
        icon="bx-list-ul"
        class=""
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
        class=""
        title="Create a webpage" 
        description="Set up a new page for data extraction"
      >
        <div class="flex-col">
          <InlineMessage 
            :text="createError" 
            :interaction="true"
            @close="createError = ''"
            v-if="createError"
          />
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
        </div>
      </BasicCard>
    </div>
  </div>
</template>

<script>
import BasicCard from '@/components/BasicCard.vue';
import InlineMessage from '@/components/InlineMessage.vue';
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
    InlineMessage,
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
      createError: "",
      targetUrl: "",
      iframeLoaded: false,          // flag to avoid re‑attaching listeners
      webpages: []
    };
  },
  methods: {
    async createWebpage() {
      try {
        const response = await fastApi.webpages.post(this.createWebpageParams);
        if (response) {
          await this.fetchWebpages();
          this.createWebpageParams = {};
        }
      } catch(e) {
        this.createError = e.response.data.detail[0].msg;
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
.webpages-view-grid {
  display: grid;
  grid-template-columns: 4fr 2fr
}
@media(max-width: 1000px) {
 .webpages-view-grid {
  grid-template-columns: 1fr;
 }
}
</style>