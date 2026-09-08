// Offline template test harness. This is NOT Hugo or a HugoBlox integration build.
// It renders the project's unmodified templates with a small, explicit helper set.
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "html/template"
    "net/url"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

type Input struct {
    Root string `json:"root"`
    Output string `json:"output"`
    BaseURL string `json:"base_url"`
    Pages []map[string]any `json:"pages"`
    Markdown map[string]string `json:"markdown"`
}

func main() {
    if len(os.Args) != 2 { panic("usage: preview_renderer input.json") }
    raw, err := os.ReadFile(os.Args[1]); must(err)
    var in Input
    must(json.Unmarshal(raw, &in))
    base, err := url.Parse(in.BaseURL); must(err)
    basePath := strings.TrimRight(base.Path, "/")
    templates := map[string]*template.Template{}
    funcs := template.FuncMap{}
    funcs["dict"] = func(args ...any) (map[string]any, error) {
        if len(args)%2 != 0 { return nil, fmt.Errorf("dict requires key/value pairs") }
        out := map[string]any{}
        for i:=0; i<len(args); i+=2 {
            key, ok := args[i].(string); if !ok { return nil, fmt.Errorf("dict key must be string") }
            out[key]=args[i+1]
        }
        return out,nil
    }
    funcs["relURL"] = func(value string) string {
        u, e := url.Parse(value)
        if e!=nil || u.IsAbs() || u.Host!="" || strings.HasPrefix(value,"#") { return value }
        if strings.HasPrefix(value,"/") { return value }
        return basePath+"/"+value
    }
    funcs["absURL"] = func(value string) string {
        u,e:=url.Parse(value)
        if e!=nil || u.IsAbs() || u.Host!="" { return value }
        if strings.HasPrefix(value,"/") { return base.Scheme+"://"+base.Host+value }
        return strings.TrimRight(in.BaseURL,"/")+"/"+value
    }
    funcs["replace"] = strings.ReplaceAll
    funcs["markdownify"] = func(value string) (template.HTML,error) {
        html,ok:=in.Markdown[value]
        if !ok { return "",fmt.Errorf("Markdown input was not pre-rendered") }
        return template.HTML(html),nil
    }
    funcs["sort"] = func(items []any,key,order string) []any {
        out:=append([]any{},items...)
        number:=func(item any) float64 {
            m,ok:=item.(map[string]any); if !ok { return -1 }
            n,ok:=m[key].(float64); if !ok { return -1 }; return n
        }
        sort.SliceStable(out,func(i,j int) bool {
            if order=="desc" { return number(out[i])>number(out[j]) }
            return number(out[i])<number(out[j])
        })
        return out
    }
    funcs["partial"] = func(name string,data any) (template.HTML,error) {
        t,ok:=templates[name]; if !ok { return "",fmt.Errorf("missing partial %s",name) }
        var buf bytes.Buffer
        if err:=t.Execute(&buf,data); err!=nil { return "",err }
        return template.HTML(buf.String()),nil
    }
    layoutRoot:=filepath.Join(in.Root,"layouts")
    must(filepath.WalkDir(layoutRoot,func(path string,entry os.DirEntry,e error) error {
        if e!=nil { return e }; if entry.IsDir() || !strings.HasSuffix(path,".html") { return nil }
        rel,e:=filepath.Rel(layoutRoot,path); if e!=nil { return e }
        name:=strings.TrimPrefix(filepath.ToSlash(rel),"_partials/")
        src,e:=os.ReadFile(path); if e!=nil { return e }
        t,e:=template.New(name).Funcs(funcs).Parse(string(src)); if e!=nil { return e }
        templates[name]=t; return nil
    }))
    for _,page:=range in.Pages {
        page["Content"]=template.HTML(page["Content"].(string))
        relative:=page["output"].(string)
        name:=page["template"].(string)
        target:=filepath.Join(in.Output,relative)
        must(os.MkdirAll(filepath.Dir(target),0755))
        f,e:=os.Create(target); must(e)
        e=templates[name].Execute(f,page); closeErr:=f.Close(); must(e); must(closeErr)
        fmt.Println("Rendered",relative)
    }
}
func must(err error) { if err!=nil { fmt.Fprintln(os.Stderr,err); os.Exit(1) } }
