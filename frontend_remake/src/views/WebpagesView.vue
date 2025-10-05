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
        <FormWebpage @success="fetchWebpages"/>
      </BasicCard>
    </div>
  </div>
</template>

<script>
import BasicCard from '@/components/CardBasic.vue';
import ListEntry from '@/components/ListEntry.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import TextInput from '@/components/TextInput.vue'
import { fastApi } from '@/utils/fastApi';
import FormWebpage from '@/components/FormWebpage.vue'

export default {
  name: 'App',
  components: {
    BasicCard,
    ListingPlaceholder,
    TextInput,
    ListEntry,
    FormWebpage,
  },
  data() {
    return {
      webpages: []
    };
  },
  methods: {
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