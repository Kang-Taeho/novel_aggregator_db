const dbName = "novels";
const colName = "novel_meta";
const db = connect("mongodb://127.0.0.1:27017/" + dbName);
db[colName].createIndex({ keywords: 1 });
db[colName].createIndex({ title: 1, author_name: 1 });
db[colName].createIndex({ description: "text", keywords: "text" });

print(`Mongo initialized: db=${dbName}, collection=${colName}`);
