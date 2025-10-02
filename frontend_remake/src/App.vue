<template>
    <header>
        <div class="name">
            <router-link to="/" class="no-deco vertical-align gap-4">
                <i class="bx bxs-server"></i>
                <span>Web Scraper Dashboard</span>
            </router-link>
        </div>
        <nav class="flex-rw gap-8">
            <router-link 
                v-for="link in links"
                class="btn btn-text no-deco vertical-align gap-4" 
                :to="link.path"
            >
                <i class="bx" :class="link.icon"></i>
                <span>{{ link.name }}</span>
            </router-link>
        </nav>
    </header>

    <main>
        <RouterView/>
    </main>

    <footer>
        Footer placeholder
    </footer>
</template>

<script>
export default {
    data() {
        return {
            links: [
                {
                    icon: 'bx-globe',
                    name: 'Webpages',
                    path: '/webpages'
                },
                {
                    icon: 'bx-target-lock',
                    name: 'Scrapes',
                    path: '/scrapes'
                },
            ]
        }
    }
}
</script>

<style scoped>

header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    gap: 8px;
    background-color: hsla(0, 0%, 100%, 0.2);
    padding-inline: var(--gutter-width);
    border-bottom: 2px solid var(--color-neutral-200);
    height: var(--header-height);
    backdrop-filter: blur(20px);
}

.name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: var(--fs-3);
    white-space: nowrap;
}
.name a {
    color: var(--color-primary-500);
    font-size: var(--fs-4);
    font-weight: var(--fw-semibold);
}

.name i {
    font-size: var(--fs-6);
    color: var(--color-primary-500);
}

main {
    padding-top: 16px;
    padding-bottom: 64px;
}

nav {
    overflow-x: scroll;
}

footer {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: auto;
    margin-bottom: 0;
    color: var(--color-neutral-500);
    padding: 8px;
}

.btn.router-link-active {
    color: var(--text-light-primary);
    background-color: var(--color-primary-500);    
}
.btn.router-link-active:hover {
    background-color: var(--color-primary-600);
}
</style>