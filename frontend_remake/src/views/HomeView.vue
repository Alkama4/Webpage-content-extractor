<template>
  <div id="app">
    <h1>Add new scrapes page??</h1>
    <div>
      <h2>1. Load page</h2>
      <div class="load-options">
        <div>
          <h3>Existing webpages</h3>
          <div 
            v-for="(webpage, index) in webpages" 
            :key="index" 
            class="webpage-option"
            @click="loadExisting(webpage.url)"
          >
            <strong>{{ webpage.page_name }}</strong>
            <span>{{ webpage.url }}</span>

            <!-- Dummy buttons -->
            <div>
              <button @click.stop>Edit</button>
              <button @click.stop>Delete</button>
            </div>
          </div>
        </div>
  
        <form @submit.prevent="createWebpage">
          <h3>Create a webpage</h3>
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
      </div>
    </div>

    <div>
      <h2>2. Select element <span v-if="targetUrl">- {{ targetUrl }}</span></h2>
      <iframe
        id="previewFrame"
        ref="previewIframe"
        :srcdoc="previewHtml"
        frameborder="0"
      ></iframe>
    </div>

    <div>
      <h2>3. Inspect details</h2>
      <div v-if="clickedElement">
        <table class="details-table">
          <tbody>
            <tr>
              <th>Element:</th>
              <td>{{ clickedElement.localName }}</td>
            </tr>
            <tr>
              <th>Locator string:</th>
              <td>{{ locator }}</td>
            </tr>
            <tr>
              <th>Inner HTML:</th>
              <td>{{ clickedElement.innerHTML }}</td>
            </tr>
            <tr>
              <th>Parsed value:</th>
              <td>{{ parseNumber(clickedElement.innerHTML) ?? '[Unable to parse]' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else>
        No element selected
      </div>
    </div>
  </div>
</template>

<script>
import { fastApi } from '@/utils/fastApi';

export default {
  name: 'App',
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
    async loadExisting(url) {
      this.targetUrl = url;
      await this.callValidate();
    },

    async loadNew() {
      this.targetUrl = this.inputUrl;
      await this.callValidate();
    },

    /** Load preview HTML from the API */
    async callValidate() {
      const url = this.targetUrl;                 // use the bound data property
      try {
        this.previewHtml = await fastApi.preview.get({
          url: url
        });
        this.iframeLoaded = false;                // new content → re‑attach listeners
      } catch (e) {
        console.error(e);
        this.previewHtml =
          '<p style="color:red;">Error loading preview</p>';
      }
    },

    async createWebpage() {
      const response = await fastApi.webpages.post(this.createWebpageParams);
      if (response) {
        await this.fetchWebpages();
      }
    },

    /** Build a simple CSS selector for an element */
    buildLocator(el) {                           // removed type annotation for Vue 3 Options API
      const parts = [];
      let current = el;

      while (current && current.nodeName.toLowerCase() !== 'html') {
        if (current === document.body) break;     // stop at body

        const tag = current.tagName.toLowerCase();
        let part = `${tag}`;

        // Add class selectors – join with '.' if multiple
        if (current.classList.length > 0) {
          part += `:${Array.from(current.classList).join('.')}`;
        }

        // Add id selector if present
        if (current.id) {
          part += `:${current.id}`;
        }

        parts.unshift(part);                     // prepend so that the order is from body → target
        current = current.parentElement;
      }
      return `${parts.join(' > ')}`;
    },

    /** Attach event listeners to the iframe once it has loaded */
    attachIframeListener() {
      const iframe = this.$refs.previewIframe;   // correct access via $refs
      if (!iframe) return;

      iframe.addEventListener('load', () => {
        const doc = iframe.contentDocument;
        if (!doc || this.iframeLoaded) return;

        // Hover outline
        const style = doc.createElement('style');
        style.textContent = `
          * { cursor: pointer; }
          :hover { outline: 2px solid orange !important; }
        `;
        doc.head.appendChild(style);

        // Click handler – store the element & locator
        doc.addEventListener('click', (e) => {
          const target = e.target;
          this.clickedElement = target;
          this.locator = this.buildLocator(target);   // compute locator
        });

        this.iframeLoaded = true;
      });
    },

    async fetchWebpages() {
      this.webpages = await fastApi.webpages.get()
    },

    parseNumber(raw) {
      let s = raw.trim();

      // keep digits, commas, dots, spaces, plus/minus
      let cleaned = s.replace(/[^\d.,+\- ]/g, "");
      cleaned = cleaned.replace(/[\s,]/g, "");

      if (!cleaned) {
        return null;
      }

      let num = Number(cleaned);
      if (isNaN(num)) {
        return null;
      }

      return num;
    }
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
iframe {
  width:100%; 
  height: 800px;
  padding: 8px;
  border: 1px solid black;
  box-sizing: border-box;
}

.details-table {
  text-align: left;
}

.load-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.webpage-option {
  padding: 2px 4px;
  border: 1px solid rgba(77, 77, 77, 0.459);
  display: flex;
  flex-direction: column;
  cursor: pointer;
}
.webpage-option:hover {
  background-color: rgba(77, 77, 77, 0.247);
}

form {
  display: flex;
  flex-direction: column;
}
</style>
