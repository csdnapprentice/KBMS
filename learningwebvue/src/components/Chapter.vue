<template>
  <ul class="chapter-list">
    <li
      v-for="node in nodes"
      :key="node.title"
      class="chapter-item"
    >
      {{ node.title }}
      <Chapter
        v-if="node.children?.length"
        :nodes="node.children"
        class="nested-chapters"
      />
    </li>
  </ul>
</template>

<script>
export default {
  name: 'Chapter',
  props: {
    nodes: {
      type: Array,
      required: true,
      validator: (value) => {
        return value.every(node => node.title && (node.children ? Array.isArray(node.children) : true))
      }
    }
  }
}
</script>

<style scoped>
.chapter-list {
  padding-left: 1.5em;
  list-style-type: none;
}

.chapter-item {
  margin: 0.5em 0;
  transition: all 0.3s ease;
}

.chapter-item:hover {
  color: #42b983;
  cursor: pointer;
}

.nested-chapters {
  margin-top: 0.3em;
}
</style>