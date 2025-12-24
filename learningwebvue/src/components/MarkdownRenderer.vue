<template>
  <div
      v-html="renderedMarkdown"
      @copy="handleCopy"
      ref="markdownContainer"
  ></div>
</template>

<script>
import MarkdownIt from 'markdown-it'
import TurndownService from 'turndown'
import katex from '@vscode/markdown-it-katex'
import 'katex/dist/katex.min.css'
import 'katex/contrib/mhchem'
import 'katex/contrib/copy-tex'
import emoji from "markdown-it-emoji";
import deflist from "markdown-it-deflist";
import abbr from "markdown-it-abbr";
import footnote from "markdown-it-footnote";
import ins from "markdown-it-ins";
import mark from "markdown-it-mark";
import taskLists from "markdown-it-task-lists";
import container from "markdown-it-container";
import toc from "markdown-it-toc-done-right";
import mermaid from "@wekanteam/markdown-it-mermaid";
import table from "markdown-it-multimd-table"
var config = {
  html: true,
  xhtmlOut: true,
  breaks: true,
  langPrefix: "lang-",
  linkify: false,
  typographer: true,
  quotes: "“”‘’",
};


const md = new MarkdownIt(config)
    .use(katex)
    .use(emoji)
    .use(deflist)
    .use(abbr)
    .use(footnote)
    .use(ins)
    .use(mark)
    .use(taskLists)
    .use(container)
    .use(container, "hljs-left")
    .use(container, "hljs-center")
    .use(container, "hljs-right")
    .use(toc)
    .use(mermaid)
    .use(table);


// 配置turndown服务
const turndownService = new TurndownService({
  headingStyle: 'atx',
  bulletListMarker: '-',
  codeBlockStyle: 'fenced',
  emDelimiter: '*',
  strongDelimiter: '**',
  linkStyle: 'inlined'
})

export default {
  props: {
    content: String
  },
  computed: {
    renderedMarkdown() {
      return md.render(this.content)
    }
  },
  methods: {
    handleCopy(event) {
      event.preventDefault()
      const selection = window.getSelection()

      // 如果有选中文本
      if (selection.toString().length > 0) {
        const range = selection.getRangeAt(0)
        const fragment = range.cloneContents()
        const tempDiv = document.createElement('div')
        tempDiv.appendChild(fragment)

        // 使用turndown转换HTML为Markdown
        const markdownText = turndownService.turndown(tempDiv.innerHTML)

        // 写入剪贴板
        event.clipboardData.setData('text/plain', markdownText)
      } else {
        // 如果没有选中文本，复制整个内容
        event.clipboardData.setData('text/plain', this.content)
      }
    }
  }
}
</script>