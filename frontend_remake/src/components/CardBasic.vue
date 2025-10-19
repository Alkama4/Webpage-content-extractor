<template>
    <div class="card-basic card">
        <div class="header-row">
            <div class="header">
                <i class="bx" :class="icon"></i>
                <span>{{ title }}</span>
            </div>
            <div class="desc">{{ description }}</div>
        </div>
        <slot></slot>
    </div>
</template>

<script>
export default {
  name: 'CardBasic',
  props: {
    title: { type: String, default: 'Untitled' },
    description: { type: String, default: 'Untitled' },
    icon: { type: String, default: 'bxs-grid' }
  }
}
</script>

<style scoped>
.card {
    display: flex;
    flex-direction: column;
    background: var(--color-neutral-50);
    border: 1px solid var(--color-neutral-200);
    border-radius: 28px;
    box-shadow: var(--shadow-sm);
    transition: all var(--t-fast);
    position: relative;
    overflow: hidden;
}

.card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-3px);
    border-color: var(--color-primary-200);
}

.card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--color-primary-500), var(--color-primary-400));
    opacity: 0;
    transition: opacity var(--t-fast);
}

.card:hover::before {
    opacity: 1;
}

.header {
    color: var(--text-dark-primary);
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: var(--fs-4);
    font-weight: var(--fw-bold);
    margin-bottom: 4px;
}
.header i {
    font-size: var(--fs-5);
    color: var(--color-primary-500);
    transition: color var(--t-fast);
}
.card:hover .header i {
    color: var(--color-primary-600);
}
.desc {
    color: var(--text-dark-secondary);
    font-size: var(--fs-2);
    line-height: 1.5;
    margin-bottom: 1.5rem;
}

.header-row {
    margin-bottom: 1rem;
}

</style>