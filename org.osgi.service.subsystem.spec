Name:		org.osgi.service.subsystem
Version:	1.1.0
Release:	1
Summary:	OSGi Subsystem Service API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.subsystem/%{version}/org.osgi.service.subsystem-%{version}-sources.jar

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:osgi.core)
BuildRequires:	mvn(org.osgi:org.osgi.annotation.versioning)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi Subsystem Service 1.1. Subsystem, its lifecycle states, and
SubsystemPermission use BundleContext, Version, Resource, Filter,
FrameworkUtil, and InvalidSyntaxException from OSGi Core 6.
IdentityNamespace is referenced from documentation only. The package
version is 1.1. Versioning annotations are compile-time only. This
build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
mkdir -p src/main/java src/main/resources/org/osgi/service/subsystem
mv org/osgi/service/subsystem/packageinfo src/main/resources/org/osgi/service/subsystem/packageinfo
mv org src/main/java/
python - <<'PY'
from pathlib import Path

root = Path("src/main/java/org/osgi/service/subsystem")
names = sorted(path.name for path in root.glob("*.java"))
expect = [
    "Subsystem.java",
    "SubsystemConstants.java",
    "SubsystemException.java",
    "SubsystemPermission.java",
    "package-info.java",
]
if names != expect:
    raise SystemExit("java files " + " ".join(names))
text = (root / "package-info.java").read_text(encoding="utf-8")
if '@Version("1.1")' not in text:
    raise SystemExit("package-info version changed")
info = Path("src/main/resources/org/osgi/service/subsystem/packageinfo")
if info.read_bytes() != b"version 1.1\n":
    raise SystemExit("packageinfo " + repr(info.read_bytes()))
if list(Path("src/main/java").rglob("packageinfo")):
    raise SystemExit("packageinfo still beside the sources")
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if not Path("about.html").is_file():
    raise SystemExit("missing about.html")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.service.subsystem</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.service.subsystem</name>
  <description>OSGi Subsystem Service.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.core</artifactId>
      <version>6.0.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.annotation.versioning</artifactId>
      <version>1.1.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.service.subsystem</artifactId>",
    "<artifactId>osgi.core</artifactId>",
    "<version>6.0.0</version>",
    "<artifactId>org.osgi.annotation.versioning</artifactId>",
    "<version>1.1.0</version>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "</project.build.sourceEncoding>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in (
    "junit",
    "SNAPSHOT",
    "<source>",
    "<target>",
    "<parent>",
    "felix",
    "maven-bundle-plugin",
    "<artifactId>org.osgi.framework</artifactId>",
    "<artifactId>org.osgi.resource</artifactId>",
    "projectbuild.sourceEncoding",
):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.service.subsystem-%{version}.jar --describe-module org.osgi.service.subsystem > module-describe.txt
grep -q '^org.osgi.service.subsystem' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.service.subsystem-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    names = set(zf.namelist())
    info = zf.read("org/osgi/service/subsystem/packageinfo")
required = {
    "org/osgi/service/subsystem/package-info.class",
    "org/osgi/service/subsystem/Subsystem.class",
    "org/osgi/service/subsystem/Subsystem$State.class",
    "org/osgi/service/subsystem/SubsystemConstants.class",
    "org/osgi/service/subsystem/SubsystemException.class",
    "org/osgi/service/subsystem/SubsystemPermission.class",
    "org/osgi/service/subsystem/SubsystemPermission$1.class",
    "org/osgi/service/subsystem/SubsystemPermissionCollection.class",
}
missing = sorted(required - names)
if missing:
    raise SystemExit("missing " + " ".join(missing))
if info != b"version 1.1\n":
    raise SystemExit("jar packageinfo " + repr(info))
PY

%files -f .mfiles
%doc LICENSE about.html
